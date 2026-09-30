import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farmbuddy.settings")
django.setup()

from django.test import Client

client = Client()

print("--- Testing API Endpoints ---")

# 1. Health
r = client.get("/api/health")
assert r.status_code == 200, f"Health failed: {r.status_code}"
print("[PASS] /api/health:", r.json())

# 2. Categories
r = client.get("/api/categories")
assert r.status_code == 200
cats = r.json()["categories"]
assert len(cats) == 8, f"Expected 8 categories, got {len(cats)}"
print(f"[PASS] /api/categories: {len(cats)} categories found")

# 3. Products
r = client.get("/api/products?limit=10")
assert r.status_code == 200
data = r.json()
assert data["total"] == 51, f"Expected 51 products, got {data['total']}"
assert len(data["products"]) == 10
print(f"[PASS] /api/products: {data['total']} total products, pagination verified")

# 4. Search & Filter
r = client.get("/api/products?q=milk&category=dairy")
assert r.status_code == 200
milk_prods = r.json()["products"]
assert len(milk_prods) > 0
print(f"[PASS] /api/products search filter: {len(milk_prods)} matches for 'milk'")

# 5. Product Detail
r = client.get("/api/products/telangana-sarvapindi")
assert r.status_code == 200
p = r.json()["product"]
assert p["slug"] == "telangana-sarvapindi"
print(f"[PASS] /api/products/<slug>: {p['name']} (INR {p['price']})")

# 6. Auth Login (Admin)
r = client.post("/api/auth/login", data={"email": "admin@farmbuddy.in", "password": "FarmBuddy@2026"}, content_type="application/json")
assert r.status_code == 200
admin_data = r.json()["user"]
assert admin_data["role"] == "admin"
print(f"[PASS] /api/auth/login (Admin): {admin_data['name']} logged in")

# 7. Auth Login (Customer)
r = client.post("/api/auth/login", data={"email": "customer@farmbuddy.in", "password": "Village@2026"}, content_type="application/json")
assert r.status_code == 200
cust_data = r.json()["user"]
assert cust_data["role"] == "customer"
print(f"[PASS] /api/auth/login (Customer): {cust_data['name']} logged in")

# 8. Cart
r = client.post("/api/cart", data={"productId": p["id"], "weight": "500g", "quantity": 2}, content_type="application/json")
assert r.status_code == 201
print("[PASS] /api/cart POST: item added")

r = client.get("/api/cart")
assert r.status_code == 200
cart_items = r.json()["items"]
assert len(cart_items) > 0
print(f"[PASS] /api/cart GET: {len(cart_items)} item(s) in basket, price: INR {cart_items[0]['price']}")

# 9. Admin stats
admin_client = Client()
admin_client.post("/api/auth/login", data={"email": "admin@farmbuddy.in", "password": "FarmBuddy@2026"}, content_type="application/json")
r = admin_client.get("/api/admin/stats")
assert r.status_code == 200
stats = r.json()
print(f"[PASS] /api/admin/stats: Total orders={stats['totalOrders']}, Revenue=INR {stats['revenue']}, Products={stats['products']}")

print("\n--- ALL BACKEND TESTS PASSED SUCCESSFULLY! ---")
