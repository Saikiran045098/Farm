import uuid
from django.db import models


def generate_uuid():
    return str(uuid.uuid4())


class Category(models.Model):
    slug = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    telugu_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    image = models.CharField(max_length=500, default="/images/grains.jpg")
    icon = models.CharField(max_length=50, default="Wheat")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def to_dict(self):
        return {
            "slug": self.slug,
            "name": self.name,
            "teluguName": self.telugu_name,
            "description": self.description,
            "image": self.image,
            "icon": self.icon,
        }


class Product(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    slug = models.CharField(max_length=150, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    telugu_name = models.CharField(max_length=200)
    description = models.TextField()
    telugu_description = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", db_column="category"
    )
    price = models.IntegerField()
    original_price = models.IntegerField(null=True, blank=True)
    weight = models.CharField(max_length=50)
    weights = models.JSONField(default=list)
    image = models.TextField()
    stock = models.IntegerField(default=50)
    farmer = models.CharField(max_length=150, default="FarmBuddy Collective")
    village = models.CharField(max_length=150, default="Siddipet, Telangana")
    ingredients = models.JSONField(default=list)
    rating = models.CharField(max_length=10, default="4.8")
    reviews = models.IntegerField(default=24)
    badge = models.CharField(max_length=60, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_organic = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "teluguName": self.telugu_name,
            "description": self.description,
            "teluguDescription": self.telugu_description,
            "category": self.category_id,
            "price": self.price,
            "originalPrice": self.original_price,
            "weight": self.weight,
            "weights": self.weights if self.weights else [self.weight],
            "image": self.image,
            "stock": self.stock,
            "farmer": self.farmer,
            "village": self.village,
            "ingredients": self.ingredients if self.ingredients else [],
            "rating": str(self.rating),
            "reviews": self.reviews,
            "badge": self.badge,
            "isFeatured": self.is_featured,
            "isOrganic": self.is_organic,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class UserAccount(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True, default="")
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default="customer")  # "admin" or "customer"
    addresses = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    def to_safe_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "addresses": self.addresses or [],
        }


class CartItem(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    owner = models.CharField(max_length=100, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    weight = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ("owner", "product", "weight")

    def __str__(self):
        return f"CartItem({self.owner}, {self.product.name}, {self.weight} x {self.quantity})"


class Order(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    owner = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(UserAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    items = models.JSONField(default=list)
    shipping_address = models.JSONField(default=dict)
    subtotal = models.IntegerField()
    delivery_fee = models.IntegerField()
    discount = models.IntegerField(default=0)
    total = models.IntegerField()
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, default="pending")
    order_status = models.CharField(max_length=50, default="Confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} - {self.customer_name} (₹{self.total})"

    def to_dict(self):
        return {
            "id": self.id,
            "owner": self.owner,
            "userId": self.user_id,
            "customerName": self.customer_name,
            "email": self.email,
            "phone": self.phone,
            "items": self.items or [],
            "shippingAddress": self.shipping_address or {},
            "subtotal": self.subtotal,
            "deliveryFee": self.delivery_fee,
            "discount": self.discount,
            "total": self.total,
            "paymentMethod": self.payment_method,
            "paymentStatus": self.payment_status,
            "orderStatus": self.order_status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Subscription(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="subscriptions")
    quantity = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    address = models.TextField()
    status = models.CharField(max_length=50, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "quantity": self.quantity,
            "frequency": self.frequency,
            "address": self.address,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Newsletter(models.Model):
    email = models.EmailField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class WishlistItem(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    owner = models.CharField(max_length=100, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        unique_together = ("owner", "product")

    def __str__(self):
        return f"Wishlist({self.owner}, {self.product.name})"
