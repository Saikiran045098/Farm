from django.contrib import admin
from .models import (
    Category,
    Product,
    UserAccount,
    CartItem,
    Order,
    Subscription,
    Newsletter,
    ContactMessage,
    WishlistItem,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "telugu_name", "slug")
    search_fields = ("name", "telugu_name", "slug")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "farmer", "is_featured", "is_organic")
    list_filter = ("category", "is_featured", "is_organic")
    search_fields = ("name", "telugu_name", "farmer", "village", "slug")


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("name", "email", "phone")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "total", "payment_method", "payment_status", "order_status", "created_at")
    list_filter = ("order_status", "payment_status", "payment_method")
    search_fields = ("id", "customer_name", "email", "phone")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quantity", "frequency", "status", "created_at")
    list_filter = ("frequency", "status")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
    search_fields = ("email",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("owner", "product", "weight", "quantity")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("owner", "product")
