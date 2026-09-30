import re
import uuid
import datetime
import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import F
from .models import UserAccount, CartItem, WishlistItem

JWT_SECRET = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
JWT_ALGORITHM = "HS256"


def hash_pwd(raw_password: str) -> str:
    return make_password(raw_password)


def verify_pwd(raw_password: str, hashed_password: str) -> bool:
    return check_password(raw_password, hashed_password)


def create_token(user: UserAccount) -> str:
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(request) -> UserAccount | None:
    token = request.COOKIES.get("fb_session")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return UserAccount.objects.filter(id=user_id).first()
    except Exception:
        return None


def sign_in_user(user: UserAccount, response, request=None):
    token = create_token(user)
    # Set httpOnly cookie
    response.set_cookie(
        "fb_session",
        token,
        max_age=7 * 24 * 3600,
        httponly=True,
        samesite="Lax",
        secure=request.is_secure() if request else False,
        path="/",
    )

    # Merge guest items if request has fb_guest
    if request:
        guest_id = request.COOKIES.get("fb_guest") or request.headers.get("x-guest-id")
        if guest_id and guest_id != user.id:
            # Merge cart
            guest_cart = CartItem.objects.filter(owner=guest_id)
            for item in guest_cart:
                existing = CartItem.objects.filter(
                    owner=user.id, product=item.product, weight=item.weight
                ).first()
                if existing:
                    existing.quantity = min(existing.quantity + item.quantity, 20)
                    existing.save()
                else:
                    CartItem.objects.create(
                        owner=user.id,
                        product=item.product,
                        weight=item.weight,
                        quantity=item.quantity,
                    )
            guest_cart.delete()

            # Merge wishlist
            guest_wishlist = WishlistItem.objects.filter(owner=guest_id)
            for w in guest_wishlist:
                if not WishlistItem.objects.filter(owner=user.id, product=w.product).exists():
                    WishlistItem.objects.create(owner=user.id, product=w.product)
            guest_wishlist.delete()

    return user.to_safe_dict()


def sign_out_user(response):
    response.delete_cookie("fb_session", path="/")


def get_owner(request, response=None) -> str:
    user = get_current_user(request)
    if user:
        return user.id

    guest = request.COOKIES.get("fb_guest") or request.headers.get("x-guest-id")
    if guest and re.match(r"^[a-zA-Z0-9_-]{10,64}$", guest):
        return guest

    new_guest = str(uuid.uuid4())
    if response is not None:
        response.set_cookie(
            "fb_guest",
            new_guest,
            max_age=30 * 24 * 3600,
            httponly=True,
            samesite="Lax",
            secure=request.is_secure() if request else False,
            path="/",
        )
    return new_guest


def weight_number(weight_str: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", weight_str)
    if not match:
        return 1.0
    val = float(match.group(1))
    if re.search(r"kg|^\d+l$", weight_str, re.IGNORECASE) and not weight_str.lower().endswith("ml"):
        return val * 1000.0
    return val


def calculate_weighted_price(base_price: int, base_weight: str, target_weight: str) -> int:
    base_n = weight_number(base_weight)
    target_n = weight_number(target_weight)
    if base_n <= 0:
        return base_price
    return round(base_price * target_n / base_n)
