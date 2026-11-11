from decimal import Decimal
from .sentiment import predict_sentiment
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm
from .models import Category, Order, OrderItem, Product, Review, SupplierLink



def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category", "seller")
    selected = request.GET.get("category")
    if selected:
        products = products.filter(category_id=selected)
    context = {
        "products": products,
        "categories": Category.objects.all(),
        "selected": selected,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = list(product.reviews.select_related("user"))
    pos = 0
    for r in reviews:
        r.sentiment = predict_sentiment(r.comment)
        if r.sentiment == "positive":
            pos += 1
    pos_percent = round(100 * pos / len(reviews)) if reviews else None
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "reviews": reviews, "pos_percent": pos_percent},
    )


def _get_cart(request):
    return request.session.setdefault("cart", {})


def _cart_items(request):
    cart = _get_cart(request)
    products = Product.objects.filter(pk__in=cart.keys(), is_active=True)
    items = []
    total = Decimal("0")
    for p in products:
        qty = cart[str(p.pk)]
        subtotal = p.price * qty
        total += subtotal
        items.append({"product": p, "quantity": qty, "subtotal": subtotal})
    return items, total


def cart_detail(request):
    items, total = _cart_items(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    if product.stock <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect("shop:product_detail", pk=pk)
    cart = _get_cart(request)
    key = str(product.pk)
    cart[key] = min(cart.get(key, 0) + 1, product.stock)
    request.session.modified = True
    return redirect("shop:cart")


@require_POST
def cart_remove(request, pk):
    cart = _get_cart(request)
    cart.pop(str(pk), None)
    request.session.modified = True
    return redirect("shop:cart")


@login_required
@require_POST
def checkout(request):
    items, total = _cart_items(request)
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart")
    try:
        with transaction.atomic():
            order = Order.objects.create(buyer=request.user)
            for item in items:
                product = Product.objects.select_for_update().get(pk=item["product"].pk)
                if product.stock < item["quantity"]:
                    raise ValueError(f"Not enough stock for {product.name}.")
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    unit_price=product.price,
                )
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("shop:cart")
    request.session["cart"] = {}
    return redirect("shop:order_detail", pk=order.pk)


@login_required
def order_list(request):
    orders = request.user.orders.order_by("-created_at")
    return render(request, "shop/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    items = order.items.select_related("product")
    total = sum(i.quantity * i.unit_price for i in items)
    return render(request, "shop/order_detail.html", {"order": order, "items": items, "total": total})


SELLER_ROLES = ("seller", "wholesaler", "manufacturer")


def _seller_required(user):
    if user.role not in SELLER_ROLES:
        raise PermissionDenied


@login_required
def seller_products(request):
    _seller_required(request.user)
    products = request.user.products.order_by("-created_at")
    return render(request, "shop/seller_products.html", {"products": products})


@login_required
def product_create(request):
    _seller_required(request.user)
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        product.save()
        return redirect("shop:seller_products")
    return render(request, "shop/product_form.html", {"form": form, "title": "Add product"})


@login_required
def product_edit(request, pk):
    _seller_required(request.user)
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("shop:seller_products")
    return render(request, "shop/product_form.html", {"form": form, "title": "Edit product"})


@login_required
@require_POST
def review_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    has_bought = OrderItem.objects.filter(order__buyer=request.user, product=product).exists()
    if not has_bought:
        messages.error(request, "Only buyers of this product can review it.")
        return redirect("shop:product_detail", pk=pk)
    try:
        rating = int(request.POST.get("rating", 0))
    except ValueError:
        rating = 0
    if not 1 <= rating <= 5:
        messages.error(request, "Please choose a rating between 1 and 5.")
        return redirect("shop:product_detail", pk=pk)
    Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={"rating": rating, "comment": request.POST.get("comment", "").strip()},
    )
    return redirect("shop:product_detail", pk=pk)
@login_required
@require_POST
def product_delete(request, pk):
    _seller_required(request.user)
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    try:
        product.delete()
        messages.success(request, "Product deleted.")
    except ProtectedError:
        product.is_active = False
        product.save(update_fields=["is_active"])
        messages.info(request, "This product has orders, so it was hidden instead of deleted.")
    return redirect("shop:seller_products")


@login_required
def seller_orders(request):
    _seller_required(request.user)
    items = (
        OrderItem.objects.filter(product__seller=request.user)
        .select_related("order", "order__buyer", "product")
        .order_by("-order__created_at")
    )
    return render(request, "shop/seller_orders.html", {"items": items})


User = get_user_model()
SUPPLIER_ROLES = ("wholesaler", "manufacturer")


@login_required
def suppliers(request):
    role = request.user.role
    if role == "seller":
        if request.method == "POST":
            sup = User.objects.filter(pk=request.POST.get("supplier"), role__in=SUPPLIER_ROLES).first()
            if sup:
                SupplierLink.objects.get_or_create(seller=request.user, supplier=sup)
            return redirect("shop:suppliers")
        linked = request.user.suppliers.values_list("supplier_id", flat=True)
        ctx = {
            "links": request.user.suppliers.select_related("supplier"),
            "available": User.objects.filter(role__in=SUPPLIER_ROLES).exclude(pk__in=linked),
        }
    elif role in SUPPLIER_ROLES:
        if request.method == "POST":
            SupplierLink.objects.filter(pk=request.POST.get("link"), supplier=request.user).update(approved=True)
            return redirect("shop:suppliers")
        ctx = {"links": request.user.clients.select_related("seller")}
    else:
        return redirect("shop:product_list")
    return render(request, "shop/suppliers.html", ctx)
