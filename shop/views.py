from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings
from django.shortcuts import get_object_or_404,  render
from decimal import Decimal

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, Product

ML_DIR = Path(settings.BASE_DIR) / "ml"
yelp_model = joblib.load(ML_DIR / "yelp_model.joblib")
yelp_vectorizer = joblib.load(ML_DIR / "yelp_vectorizer.joblib")
fraud_model = joblib.load(ML_DIR / "fraud_model.joblib")
fraud_data = pd.read_csv(Path(settings.BASE_DIR) / "data" / "fraud" / "creditcard.csv")


def review(request):
    result = None
    text = ""
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            X = yelp_vectorizer.transform([text])
            result = yelp_model.predict(X)[0]
    return render(request, "shop/review.html", {"result": result, "text": text})


def fraud(request):
    result = None
    if request.method == "POST":
        row = fraud_data.sample(n=1)
        actual = int(row["Class"].iloc[0])
        X = row.drop("Class", axis=1)
        prob = float(fraud_model.predict_proba(X)[0][1])
        result = {
            "amount": round(float(row["Amount"].iloc[0]), 2),
            "probability": round(prob * 100, 2),
            "predicted": "Fraud" if prob >= 0.5 else "Normal",
            "actual": "Fraud" if actual == 1 else "Normal",
        }
    return render(request, "shop/fraud.html", {"result": result})

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category", "seller")
    return render(request, "shop/product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        qty = max(1, int(request.GET.get("qty", 1)))
    except ValueError:
        qty = 1
    is_wholesale = qty >= product.min_wholesale_qty
    unit_price = product.get_unit_price(qty, wholesale=is_wholesale)
    context = {
        "product": product,
        "tiers": product.price_tiers.all(),
        "qty": qty,
        "is_wholesale": is_wholesale,
        "unit_price": unit_price,
        "total": unit_price * qty,
    }
    return render(request, "shop/product_detail.html", context) 

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("product_list")
    return render(request, "registration/signup.html", {"form": form})


def _build_cart(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0")
    for pid, qty in cart.items():
        product = Product.objects.filter(pk=pid, is_active=True).first()
        if not product:
            continue
        is_wholesale = qty >= product.min_wholesale_qty
        unit_price = product.get_unit_price(qty, wholesale=is_wholesale)
        line_total = unit_price * qty
        items.append({
            "product": product,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total,
            "is_wholesale": is_wholesale,
        })
        total += line_total
    return items, total


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        qty = max(1, int(request.POST.get("qty", 1)))
    except ValueError:
        qty = 1
    cart = request.session.get("cart", {})
    new_qty = min(cart.get(str(pk), 0) + qty, product.stock)
    if new_qty < 1:
        return redirect("product_detail", pk=pk)
    cart[str(pk)] = new_qty
    request.session["cart"] = cart
    return redirect("cart_detail")


@require_POST
def cart_remove(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("cart_detail")


def cart_detail(request):
    items, total = _build_cart(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})


@login_required
@require_POST
def checkout(request):
    items, total = _build_cart(request)
    if not items:
        return redirect("cart_detail")
    try:
        with transaction.atomic():
            has_wholesale = any(i["is_wholesale"] for i in items)
            order = Order.objects.create(
                buyer=request.user,
                order_type="wholesale" if has_wholesale else "retail",
            )
            for i in items:
                product = Product.objects.select_for_update().get(pk=i["product"].pk)
                if product.stock < i["qty"]:
                    raise ValueError(f"موجودی «{product.name}» کافی نیست.")
                product.stock -= i["qty"]
                product.save(update_fields=["stock"])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=i["qty"],
                    unit_price=i["unit_price"],
                )
    except ValueError as e:
        return render(request, "shop/cart.html", {"items": items, "total": total, "error": str(e)})
    request.session["cart"] = {}
    return redirect("order_done", pk=order.pk)


@login_required
def order_done(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, "shop/order_done.html", {"order": order})