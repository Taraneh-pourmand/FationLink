from django.contrib import admin

from .models import Category, Order, OrderItem, PriceTier, Product, Review


class PriceTierInline(admin.TabularInline):
 model = PriceTier
extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
 search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
 list_display = ("name", "seller", "category", "price", "min_wholesale_qty", "stock", "is_active")
list_filter = ("is_active", "category")
search_fields = ("name", "seller__username")
inlines = [PriceTierInline]


class OrderItemInline(admin.TabularInline):
 model = OrderItem
extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
 list_display = ("id", "buyer", "order_type", "status", "fraud_score", "created_at")
list_filter = ("status", "order_type")
inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
 list_display = ("product", "user", "rating", "created_at")
list_filter = ("rating",)
