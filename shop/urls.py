from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("seller/orders/", views.seller_orders, name="seller_orders"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path("product/<int:pk>/review/", views.review_add, name="review_add"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("seller/products/", views.seller_products, name="seller_products"),
    path("seller/products/new/", views.product_create, name="product_create"),
    path("seller/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("seller/products/<int:pk>/delete/", views.product_delete, name="product_delete"),
]