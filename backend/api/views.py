import re
import json
import uuid
import datetime
from django.utils import timezone
from django.db.models import Q, F
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
from .auth_utils import (
    get_current_user,
    sign_in_user,
    sign_out_user,
    get_owner,
    hash_pwd,
    verify_pwd,
    calculate_weighted_price,
)
from .seeds import ensure_seed_data


def check_admin(request):
    user = get_current_user(request)
    if not user or user.role != "admin":
        return None
    return user


def check_auth(request):
    return get_current_user(request)


# ------------------ Health Check ------------------
@api_view(["GET"])
def health_check(request):
    ensure_seed_data()
    return Response({"ok": True, "status": "healthy", "service": "FarmBuddy Django REST API"})


# ------------------ Authentication ------------------
@api_view(["GET"])
def auth_me(request):
    user = get_current_user(request)
    return Response({"user": user.to_safe_dict() if user else None})


@api_view(["POST"])
def auth_login(request):
    ensure_seed_data()
    data = request.data
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    user = UserAccount.objects.filter(email=email).first()
    if not user or not verify_pwd(password, user.password):
        return Response({"error": "Email or password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

    res = Response({"user": user.to_safe_dict()})
    sign_in_user(user, res, request)
    return res


@api_view(["POST"])
def auth_register(request):
    ensure_seed_data()
    data = request.data
    email = str(data.get("email", "")).strip().lower()
    name = str(data.get("name", "")).strip()
    password = str(data.get("password", ""))
    phone = str(data.get("phone", "")).strip()

    if not name:
        return Response({"error": "Please enter your name"}, status=status.HTTP_400_BAD_REQUEST)
    if not email or "@" not in email:
        return Response({"error": "Please enter a valid email"}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 8:
        return Response({"error": "Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)

    if UserAccount.objects.filter(email=email).exists():
        return Response({"error": "An account with this email already exists"}, status=status.HTTP_409_CONFLICT)

    user = UserAccount.objects.create(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        phone=phone,
        password=hash_pwd(password),
        role="customer",
        addresses=[],
    )

    res = Response({"user": user.to_safe_dict()}, status=status.HTTP_201_CREATED)
    sign_in_user(user, res, request)
    return res


@api_view(["POST"])
def auth_logout(request):
    res = Response({"ok": True})
    sign_out_user(res)
    return res


# ------------------ Categories ------------------
@api_view(["GET", "POST"])
def categories_collection(request):
    ensure_seed_data()
    if request.method == "GET":
        cats = [c.to_dict() for c in Category.objects.all()]
        return Response({"categories": cats})

    # POST (Admin only)
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    slug = str(data.get("slug", "")).strip().lower()
    name = str(data.get("name", "")).strip()
    telugu_name = str(data.get("teluguName", "")).strip()

    if not slug or not name:
        return Response({"error": "Slug and name are required"}, status=status.HTTP_400_BAD_REQUEST)

    if Category.objects.filter(slug=slug).exists():
        return Response({"error": "Category slug already exists"}, status=status.HTTP_409_CONFLICT)

    cat = Category.objects.create(
        slug=slug,
        name=name,
        telugu_name=telugu_name or name,
        description=data.get("description", ""),
        image=data.get("image", "/images/grains.jpg"),
        icon=data.get("icon", "Wheat"),
    )
    return Response({"category": cat.to_dict()}, status=status.HTTP_201_CREATED)


@api_view(["PUT", "DELETE"])
def category_detail(request, slug):
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    cat = Category.objects.filter(slug=slug).first()
    if not cat:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        if cat.products.exists():
            return Response(
                {"error": "Move all products to another category before removing this category."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cat.delete()
        return Response({"ok": True})

    data = request.data
    if "name" in data:
        cat.name = data["name"]
    if "teluguName" in data:
        cat.telugu_name = data["teluguName"]
    if "description" in data:
        cat.description = data["description"]
    if "image" in data:
        cat.image = data["image"]
    if "icon" in data:
        cat.icon = data["icon"]
    cat.save()
    return Response({"category": cat.to_dict()})


# ------------------ Products ------------------
@api_view(["GET", "POST"])
def products_collection(request):
    ensure_seed_data()
    if request.method == "GET":
        qs = Product.objects.all().select_related("category")

        # Category filter
        cat = request.GET.get("category")
        if cat:
            qs = qs.filter(category_id=cat)

        # Featured filter
        featured = request.GET.get("featured")
        if featured == "true":
            qs = qs.filter(is_featured=True)

        # Search token matching
        q = request.GET.get("q", "").strip()
        if q:
            aliases = {
                "snacks": "telangana-foods",
                "foods": "telangana-foods",
                "dairy": "dairy",
                "flour": "grains",
                "flours": "grains",
                "nuts": "dry-fruits",
                "pickles": "pickles",
                "seeds": "seeds",
                "vegetables": "farm-produce",
                "produce": "farm-produce",
            }
            tokens = q.lower().split()
            for token in tokens:
                cond = (
                    Q(name__icontains=token)
                    | Q(telugu_name__icontains=token)
                    | Q(category__slug__icontains=token)
                    | Q(farmer__icontains=token)
                    | Q(village__icontains=token)
                    | Q(description__icontains=token)
                )
                if token in aliases:
                    cond |= Q(category__slug=aliases[token])
                qs = qs.filter(cond)

        # Price filters
        min_price = request.GET.get("minPrice")
        if min_price:
            try:
                qs = qs.filter(price__gte=max(0, int(min_price)))
            except ValueError:
                pass

        max_price = request.GET.get("maxPrice")
        if max_price:
            try:
                qs = qs.filter(price__lte=int(max_price))
            except ValueError:
                pass

        # Availability filter
        avail = request.GET.get("availability")
        if avail == "in":
            qs = qs.filter(stock__gte=1)
        elif avail == "out":
            qs = qs.filter(stock=0)

        # Weight filter
        weight = request.GET.get("weight")
        if weight:
            qs = qs.filter(weights__contains=[weight])

        # Sorting
        sort = request.GET.get("sort")
        if sort == "price-low":
            qs = qs.order_by("price")
        elif sort == "price-high":
            qs = qs.order_by("-price")
        elif sort == "newest":
            qs = qs.order_by("-created_at")
        else:
            qs = qs.order_by("id")

        total = qs.count()
        try:
            limit = min(100, max(1, int(request.GET.get("limit", 12))))
        except ValueError:
            limit = 12

        try:
            page = max(1, int(request.GET.get("page", 1)))
        except ValueError:
            page = 1

        start = (page - 1) * limit
        end = start + limit
        products_page = [p.to_dict() for p in qs[start:end]]
        pages = max(1, (total + limit - 1) // limit)

        return Response({
            "products": products_page,
            "total": total,
            "page": page,
            "pages": pages,
        })

    # POST (Admin only)
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    category_slug = data.get("category")
    cat = Category.objects.filter(slug=category_slug).first()
    if not cat:
        return Response({"error": "Select a valid category"}, status=status.HTTP_400_BAD_REQUEST)

    weight = data.get("weight", "500g")
    weights = data.get("weights", [weight])
    if weight not in weights:
        return Response({"error": "Available pack sizes must include the base pack size"}, status=status.HTTP_400_BAD_REQUEST)

    slug = data.get("slug", "").strip().lower()
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", data.get("name", "").lower()).strip("-")

    if Product.objects.filter(slug=slug).exists():
        return Response({"error": "Product slug already exists"}, status=status.HTTP_409_CONFLICT)

    prod = Product.objects.create(
        id=str(uuid.uuid4()),
        slug=slug,
        name=data.get("name"),
        telugu_name=data.get("teluguName", data.get("name")),
        description=data.get("description", ""),
        telugu_description=data.get("teluguDescription", ""),
        category=cat,
        price=int(data.get("price", 60)),
        original_price=int(data["originalPrice"]) if data.get("originalPrice") else None,
        weight=weight,
        weights=weights,
        image=data.get("image", "/images/grains.jpg"),
        stock=int(data.get("stock", 50)),
        farmer=data.get("farmer", "FarmBuddy Collective"),
        village=data.get("village", "Siddipet, Telangana"),
        ingredients=data.get("ingredients", []),
        rating=str(data.get("rating", "4.8")),
        reviews=int(data.get("reviews", 0)),
        badge=data.get("badge") or None,
        is_featured=bool(data.get("isFeatured", False)),
        is_organic=bool(data.get("isOrganic", True)),
    )
    return Response({"product": prod.to_dict()}, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, pk_or_slug):
    ensure_seed_data()
    prod = Product.objects.filter(Q(id=pk_or_slug) | Q(slug=pk_or_slug)).first()
    if not prod:
        return Response({"error": "This product is no longer available"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response({"product": prod.to_dict()})

    # PUT and DELETE require admin
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "DELETE":
        prod.delete()
        return Response({"ok": True})

    data = request.data
    if "name" in data:
        prod.name = data["name"]
    if "teluguName" in data:
        prod.telugu_name = data["teluguName"]
    if "slug" in data:
        prod.slug = data["slug"]
    if "category" in data:
        cat = Category.objects.filter(slug=data["category"]).first()
        if cat:
            prod.category = cat
    if "description" in data:
        prod.description = data["description"]
    if "teluguDescription" in data:
        prod.telugu_description = data["teluguDescription"]
    if "price" in data:
        prod.price = int(data["price"])
    if "originalPrice" in data:
        prod.original_price = int(data["originalPrice"]) if data["originalPrice"] else None
    if "weight" in data:
        prod.weight = data["weight"]
    if "weights" in data:
        prod.weights = data["weights"]
    if "image" in data:
        prod.image = data["image"]
    if "stock" in data:
        prod.stock = int(data["stock"])
    if "farmer" in data:
        prod.farmer = data["farmer"]
    if "village" in data:
        prod.village = data["village"]
    if "ingredients" in data:
        prod.ingredients = data["ingredients"]
    if "badge" in data:
        prod.badge = data["badge"] or None
    if "isFeatured" in data:
        prod.is_featured = bool(data["isFeatured"])
    if "isOrganic" in data:
        prod.is_organic = bool(data["isOrganic"])

    prod.save()
    return Response({"product": prod.to_dict()})


# ------------------ Cart ------------------
@api_view(["GET", "POST"])
def cart_collection(request):
    ensure_seed_data()
    res = Response()
    owner = get_owner(request, res)

    if request.method == "GET":
        items = CartItem.objects.filter(owner=owner).select_related("product")
        cart_data = []
        for item in items:
            cart_data.append({
                "id": item.id,
                "owner": item.owner,
                "productId": item.product.id,
                "weight": item.weight,
                "quantity": item.quantity,
                "price": calculate_weighted_price(item.product.price, item.product.weight, item.weight),
                "product": item.product.to_dict(),
            })
        res.data = {"items": cart_data}
        return res

    # POST (Add to Cart)
    data = request.data
    product_id = data.get("productId")
    weight = data.get("weight")
    quantity = int(data.get("quantity", 1))

    if not product_id or not weight:
        return Response({"error": "Product ID and weight are required"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        prod = Product.objects.select_for_update().filter(id=product_id).first()
        if not prod:
            return Response({"error": "Product unavailable"}, status=status.HTTP_404_NOT_FOUND)

        if weight not in prod.weights and weight != prod.weight:
            return Response({"error": "Please choose an available weight"}, status=status.HTTP_400_BAD_REQUEST)

        existing = CartItem.objects.filter(owner=owner, product=prod, weight=weight).first()
        total_qty = (existing.quantity if existing else 0) + quantity

        if total_qty > prod.stock:
            return Response({"error": f"Only {prod.stock} packs are available"}, status=status.HTTP_400_BAD_REQUEST)
        if total_qty > 20:
            return Response({"error": "You can add up to 20 packs of each product"}, status=status.HTTP_400_BAD_REQUEST)

        if existing:
            existing.quantity = total_qty
            existing.save()
            cart_item = existing
        else:
            cart_item = CartItem.objects.create(
                id=str(uuid.uuid4()),
                owner=owner,
                product=prod,
                weight=weight,
                quantity=quantity,
            )

    res.status_code = status.HTTP_201_CREATED
    res.data = {
        "item": {
            "id": cart_item.id,
            "owner": cart_item.owner,
            "productId": prod.id,
            "weight": cart_item.weight,
            "quantity": cart_item.quantity,
        }
    }
    return res


@api_view(["PUT", "DELETE"])
def cart_detail(request, pk):
    res = Response()
    owner = get_owner(request, res)

    item = CartItem.objects.filter(id=pk, owner=owner).select_related("product").first()
    if not item:
        return Response({"error": "Basket item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        item.delete()
        res.data = {"ok": True}
        return res

    quantity = int(request.data.get("quantity", 1))
    if quantity > item.product.stock:
        return Response({"error": f"Only {item.product.stock} packs are available"}, status=status.HTTP_400_BAD_REQUEST)
    if quantity < 1 or quantity > 20:
        return Response({"error": "Quantity must be between 1 and 20"}, status=status.HTTP_400_BAD_REQUEST)

    item.quantity = quantity
    item.save()
    res.data = {
        "item": {
            "id": item.id,
            "owner": item.owner,
            "productId": item.product.id,
            "weight": item.weight,
            "quantity": item.quantity,
        }
    }
    return res


# ------------------ Wishlist ------------------
@api_view(["GET", "POST"])
def wishlist_collection(request):
    ensure_seed_data()
    res = Response()
    owner = get_owner(request, res)

    if request.method == "GET":
        items = WishlistItem.objects.filter(owner=owner).select_related("product")
        res.data = {"products": [item.product.to_dict() for item in items]}
        return res

    product_id = request.data.get("productId")
    if not product_id:
        return Response({"error": "productId is required"}, status=status.HTTP_400_BAD_REQUEST)

    prod = Product.objects.filter(id=product_id).first()
    if prod:
        WishlistItem.objects.get_or_create(owner=owner, product=prod)
    res.data = {"ok": True}
    return res


@api_view(["DELETE"])
def wishlist_detail(request, product_id):
    res = Response()
    owner = get_owner(request, res)
    WishlistItem.objects.filter(owner=owner, product_id=product_id).delete()
    res.data = {"ok": True}
    return res


# ------------------ Orders ------------------
@api_view(["GET", "POST"])
def orders_collection(request):
    ensure_seed_data()
    user = get_current_user(request)
    res = Response()
    owner = get_owner(request, res)

    if request.method == "GET":
        if user and user.role == "admin":
            orders = Order.objects.all().order_by("-created_at")[:200]
        else:
            orders = Order.objects.filter(owner=owner).order_by("-created_at")[:200]
        res.data = {"orders": [o.to_dict() for o in orders]}
        return res

    # POST (Place Order)
    data = request.data
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    address = data.get("address", {})
    payment_method = data.get("paymentMethod", "Cash on Delivery")
    coupon = str(data.get("coupon", "")).strip()

    if not name or not phone or not email or not address:
        return Response({"error": "Name, phone, email, and address are required"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        cart_items = CartItem.objects.select_for_update().filter(owner=owner).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Your basket is empty. Add some village goodness first."}, status=status.HTTP_400_BAD_REQUEST)

        order_items = []
        for item in cart_items:
            prod = item.product
            if prod.stock < item.quantity:
                return Response({"error": f"{prod.name} is no longer available in this quantity"}, status=status.HTTP_400_BAD_REQUEST)

            item_price = calculate_weighted_price(prod.price, prod.weight, item.weight)
            order_items.append({
                "productId": prod.id,
                "name": prod.name,
                "teluguName": prod.telugu_name,
                "image": prod.image,
                "weight": item.weight,
                "quantity": item.quantity,
                "price": item_price,
            })
            prod.stock -= item.quantity
            prod.save()

        subtotal = sum(i["price"] * i["quantity"] for i in order_items)
        delivery_fee = 0 if subtotal >= 499 else 40
        discount = 0
        if coupon.upper() == "VILLAGE10" and subtotal >= 499:
            discount = min(100, round(subtotal * 0.1))
        total = subtotal + delivery_fee - discount

        order_id = f"FB-{hex(int(datetime.datetime.now().timestamp()))[2:].upper()}-{uuid.uuid4().hex[:4].upper()}"
        order = Order.objects.create(
            id=order_id,
            owner=owner,
            user=user if user else None,
            customer_name=name,
            email=email,
            phone=phone,
            shipping_address=address,
            items=order_items,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            total=total,
            payment_method=payment_method,
            payment_status="pending",
            order_status="Confirmed" if payment_method == "Cash on Delivery" else "Pending",
        )

        cart_items.delete()

        if user:
            user.phone = phone
            user.addresses = [address]
            user.save()

    res.status_code = status.HTTP_201_CREATED
    res.data = {"order": order.to_dict()}
    return res


@api_view(["GET"])
def order_detail(request, pk):
    user = get_current_user(request)
    owner = get_owner(request)

    qs = Order.objects.filter(id=pk)
    if not (user and user.role == "admin"):
        qs = qs.filter(owner=owner)

    order = qs.first()
    if not order:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({"order": order.to_dict()})


@api_view(["PUT"])
def order_status_update(request, pk):
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get("status")
    allowed = ["Pending", "Confirmed", "Processing", "Packed", "Out for Delivery", "Delivered", "Cancelled"]
    if new_status not in allowed:
        return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        order = Order.objects.select_for_update().filter(id=pk).first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.order_status == "Cancelled" and new_status != "Cancelled":
            return Response({"error": "Cancelled orders cannot be reopened"}, status=status.HTTP_400_BAD_REQUEST)
        if order.order_status == "Delivered" and new_status != "Delivered":
            return Response({"error": "Delivered orders cannot be changed"}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == "Cancelled" and order.order_status != "Cancelled":
            for item in order.items:
                Product.objects.filter(id=item["productId"]).update(stock=F("stock") + item["quantity"])

        order.order_status = new_status
        if new_status == "Delivered" and order.payment_method == "Cash on Delivery":
            order.payment_status = "paid"
        order.save()

    return Response({"order": order.to_dict()})


# ------------------ Subscriptions ------------------
@api_view(["GET", "POST"])
def subscriptions_collection(request):
    user = check_auth(request)
    if not user:
        return Response({"error": "Please sign in to continue"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        subs = [s.to_dict() for s in Subscription.objects.filter(user=user)]
        return Response({"subscriptions": subs})

    data = request.data
    sub = Subscription.objects.create(
        id=str(uuid.uuid4()),
        user=user,
        quantity=data.get("quantity", "1L"),
        frequency=data.get("frequency", "Daily"),
        address=data.get("address", ""),
        status="Active",
    )
    return Response({"subscription": sub.to_dict()}, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def subscription_detail(request, pk):
    user = check_auth(request)
    if not user:
        return Response({"error": "Please sign in to continue"}, status=status.HTTP_401_UNAUTHORIZED)

    sub = Subscription.objects.filter(id=pk, user=user).first()
    if not sub:
        return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)

    sub.status = request.data.get("status", sub.status)
    sub.save()
    return Response({"subscription": sub.to_dict()})


# ------------------ Newsletter & Contact ------------------
@api_view(["POST"])
def newsletter_subscribe(request):
    email = str(request.data.get("email", "")).strip().lower()
    if email and "@" in email:
        Newsletter.objects.get_or_create(email=email)
    return Response({"ok": True})


@api_view(["POST"])
def contact_message(request):
    name = str(request.data.get("name", "")).strip()
    email = str(request.data.get("email", "")).strip()
    msg = str(request.data.get("message", "")).strip()

    if not name or not email or not msg:
        return Response({"error": "Name, email, and message are required"}, status=status.HTTP_400_BAD_REQUEST)

    ContactMessage.objects.create(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        message=msg,
    )
    return Response({"ok": True}, status=status.HTTP_201_CREATED)


# ------------------ Users ------------------
@api_view(["GET"])
def users_collection(request):
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    users = UserAccount.objects.all()
    all_orders = list(Order.objects.all())
    result = []
    for u in users:
        user_orders = [o for o in all_orders if o.user_id == u.id]
        active_orders = [o for o in user_orders if o.order_status != "Cancelled"]
        spent = sum(o.total for o in active_orders)
        result.append({
            **u.to_safe_dict(),
            "createdAt": u.created_at.isoformat(),
            "orders": len(user_orders),
            "spent": spent,
        })
    return Response({"users": result})


@api_view(["GET", "PUT"])
def user_detail(request, pk):
    me = check_auth(request)
    if not me:
        return Response({"error": "Please sign in to continue"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        if me.role != "admin" and me.id != pk:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        target = UserAccount.objects.filter(id=pk).first()
        if not target:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"user": target.to_safe_dict()})

    # PUT
    if me.id != pk and me.role != "admin":
        return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

    target = UserAccount.objects.filter(id=pk).first()
    if not target:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    if "name" in data:
        target.name = data["name"]
    if "phone" in data:
        target.phone = data["phone"]
    if "addresses" in data:
        target.addresses = data["addresses"]
    target.save()
    return Response({"user": target.to_safe_dict()})


# ------------------ Admin Stats ------------------
@api_view(["GET"])
def admin_stats(request):
    if not check_admin(request):
        return Response({"error": "Administrator access required"}, status=status.HTTP_403_FORBIDDEN)

    all_orders = list(Order.objects.all().order_by("-created_at"))
    all_products = list(Product.objects.all())
    all_users = list(UserAccount.objects.all())

    active = [o for o in all_orders if o.order_status != "Cancelled"]
    today_str = datetime.date.today().isoformat()
    today_orders = len([o for o in all_orders if o.created_at and o.created_at.date().isoformat() == today_str])

    # Last 7 days sales
    sales = []
    for i in range(7):
        d = datetime.date.today() - datetime.timedelta(days=6 - i)
        d_str = d.isoformat()
        day_orders = [o for o in active if o.created_at and o.created_at.date().isoformat() == d_str]
        sales.append({
            "day": d.strftime("%a"),
            "sales": sum(o.total for o in day_orders),
            "orders": len(day_orders),
        })

    # Performance
    perf = []
    for p in all_products:
        units = sum(
            sum(i["quantity"] for i in o.items if i.get("productId") == p.id)
            for o in active
        )
        perf.append({"name": p.name, "units": units})
    perf.sort(key=lambda x: x["units"], reverse=True)

    low_stock = [p.to_dict() for p in all_products if p.stock < 10]
    recent = [o.to_dict() for o in all_orders[:6]]
    statuses = ["Pending", "Confirmed", "Processing", "Packed", "Out for Delivery", "Delivered", "Cancelled"]

    return Response({
        "totalOrders": len(all_orders),
        "revenue": sum(o.total for o in active),
        "customers": len([u for u in all_users if u.role == "customer"]),
        "products": len(all_products),
        "lowStock": low_stock,
        "todayOrders": today_orders,
        "sales": sales,
        "performance": perf[:5],
        "recentOrders": recent,
        "statuses": statuses,
    })
