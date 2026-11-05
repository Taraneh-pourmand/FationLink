from django.contrib import admin
from .models import Category, Product, PriceTier, Order, OrderItem, Review


class PriceTierInline(admin.TabularInline):
    model = PriceTier
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "seller", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    inlines = [PriceTierInline]
