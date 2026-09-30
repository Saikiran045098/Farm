from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^health/?$", views.health_check, name="health_check"),

    # Auth
    re_path(r"^auth/me/?$", views.auth_me, name="auth_me"),
    re_path(r"^auth/login/?$", views.auth_login, name="auth_login"),
    re_path(r"^auth/register/?$", views.auth_register, name="auth_register"),
    re_path(r"^auth/logout/?$", views.auth_logout, name="auth_logout"),

    # Categories
    re_path(r"^categories/?$", views.categories_collection, name="categories_collection"),
    re_path(r"^categories/(?P<slug>[a-zA-Z0-9_-]+)/?$", views.category_detail, name="category_detail"),

    # Products
    re_path(r"^products/?$", views.products_collection, name="products_collection"),
    re_path(r"^products/(?P<pk_or_slug>[a-zA-Z0-9_-]+)/?$", views.product_detail, name="product_detail"),

    # Cart
    re_path(r"^cart/?$", views.cart_collection, name="cart_collection"),
    re_path(r"^cart/(?P<pk>[a-zA-Z0-9_-]+)/?$", views.cart_detail, name="cart_detail"),

    # Wishlist
    re_path(r"^wishlist/?$", views.wishlist_collection, name="wishlist_collection"),
    re_path(r"^wishlist/(?P<product_id>[a-zA-Z0-9_-]+)/?$", views.wishlist_detail, name="wishlist_detail"),

    # Orders
    re_path(r"^orders/?$", views.orders_collection, name="orders_collection"),
    re_path(r"^orders/(?P<pk>[a-zA-Z0-9_-]+)/status/?$", views.order_status_update, name="order_status_update"),
    re_path(r"^orders/(?P<pk>[a-zA-Z0-9_-]+)/?$", views.order_detail, name="order_detail"),

    # Subscriptions
    re_path(r"^subscriptions/?$", views.subscriptions_collection, name="subscriptions_collection"),
    re_path(r"^subscriptions/(?P<pk>[a-zA-Z0-9_-]+)/?$", views.subscription_detail, name="subscription_detail"),

    # Newsletter & Contact
    re_path(r"^newsletter/?$", views.newsletter_subscribe, name="newsletter_subscribe"),
    re_path(r"^contact/?$", views.contact_message, name="contact_message"),

    # Users
    re_path(r"^users/?$", views.users_collection, name="users_collection"),
    re_path(r"^users/(?P<pk>[a-zA-Z0-9_-]+)/?$", views.user_detail, name="user_detail"),

    # Admin Stats
    re_path(r"^admin/stats/?$", views.admin_stats, name="admin_stats"),
]
