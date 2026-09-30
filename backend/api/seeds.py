import datetime
from django.utils import timezone
from .models import Category, Product, UserAccount, Order
from .auth_utils import hash_pwd

CATEGORIES_DATA = [
    { "slug": "dairy", "name": "Milk & Dairy", "telugu_name": "పాలు & పాల ఉత్పత్తులు", "description": "Fresh from our local dairy farms, every morning.", "image": "/images/milk.jpg", "icon": "Milk" },
    { "slug": "telangana-foods", "name": "Telangana Foods", "telugu_name": "తెలంగాణ రుచులు", "description": "Handmade flavours that bring you home.", "image": "/images/sarvapindi.jpg", "icon": "CookingPot" },
    { "slug": "grains", "name": "Grains & Flours", "telugu_name": "ధాన్యాలు & పిండి", "description": "Wholesome native grains from Telangana fields.", "image": "/images/grains.jpg", "icon": "Wheat" },
    { "slug": "dry-fruits", "name": "Dry Fruits", "telugu_name": "ఎండు పండ్లు", "description": "A handful of nature’s delicious goodness.", "image": "/images/almonds.jpg", "icon": "Nut" },
    { "slug": "seeds", "name": "Healthy Seeds", "telugu_name": "ఆరోగ్య విత్తనాలు", "description": "Small seeds. Naturally big on nutrition.", "image": "/images/seeds.jpg", "icon": "Sprout" },
    { "slug": "farm-produce", "name": "Farm Produce", "telugu_name": "పొలం ఉత్పత్తులు", "description": "Seasonal harvests, picked with care.", "image": "/images/vegetables.jpg", "icon": "Carrot" },
    { "slug": "pickles", "name": "Village Pickles", "telugu_name": "పల్లె పచ్చళ్లు", "description": "Family recipes in every spoonful.", "image": "/images/pickle.jpg", "icon": "Amphora" },
    { "slug": "combos", "name": "Village Combos", "telugu_name": "పల్లె కాంబోలు", "description": "Your favourites, a little better together.", "image": "/images/sakinalu.jpg", "icon": "Package" },
]

ROWS = [
    ["Fresh Cow Milk", "తాజా ఆవు పాలు", "fresh-cow-milk", "dairy", 60, "500ml", "milk", "FARM FRESH", 70],
    ["Traditional Sarvapindi", "సర్వపిండి", "telangana-sarvapindi", "telangana-foods", 120, "500g", "sarvapindi", "VILLAGE FAVOURITE", 150],
    ["Homemade Desi Ghee", "ఇంట్లో చేసిన నెయ్యి", "homemade-desi-ghee", "dairy", 449, "500g", "ghee", "PURE & NATURAL", 520],
    ["Handmade Sakinalu", "సకినాలు", "handmade-sakinalu", "telangana-foods", 149, "500g", "sakinalu", "HANDMADE", 180],
    ["Buffalo Milk", "గేదె పాలు", "fresh-buffalo-milk", "dairy", 75, "500ml", "milk", None, None],
    ["Farm Fresh Curd", "తాజా పెరుగు", "farm-fresh-curd", "dairy", 55, "500g", "milk", None, None],
    ["Spiced Buttermilk", "మజ్జిగ", "spiced-buttermilk", "dairy", 35, "500ml", "milk", None, None],
    ["White Village Butter", "వెన్న", "village-butter", "dairy", 180, "250g", "ghee", None, None],
    ["Fresh Paneer", "తాజా పనీర్", "fresh-paneer", "dairy", 120, "250g", "milk", None, None],
    ["Badam Flavoured Milk", "బాదం పాలు", "badam-milk", "dairy", 65, "500ml", "milk", None, None],
    ["Jowar Grain", "జొన్నలు", "native-jowar-grain", "grains", 85, "1kg", "grains", "NATIVE GRAINS", None],
    ["Bajra Pearl Millet", "సజ్జలు", "bajra-pearl-millet", "grains", 75, "1kg", "grains", None, None],
    ["Ragi Finger Millet", "రాగులు", "ragi-finger-millet", "grains", 95, "1kg", "grains", None, None],
    ["Telangana Sona Rice", "సన్న బియ్యం", "telangana-sona-rice", "grains", 80, "1kg", "grains", None, None],
    ["Maize Grain", "మొక్కజొన్నలు", "maize-grain", "grains", 65, "1kg", "grains", None, None],
    ["Stone-ground Jowar Flour", "జొన్న పిండి", "jowar-flour", "grains", 90, "1kg", "grains", None, None],
    ["Fresh Ragi Flour", "రాగి పిండి", "ragi-flour", "grains", 95, "1kg", "grains", None, None],
    ["Traditional Rice Flour", "బియ్యం పిండి", "rice-flour", "grains", 70, "1kg", "grains", None, None],
    ["Crispy Garelu", "గారెలు", "crispy-garelu", "telangana-foods", 110, "500g", "sarvapindi", None, None],
    ["Homemade Chekkalu", "చెక్కలు", "homemade-chekkalu", "telangana-foods", 130, "500g", "sakinalu", None, None],
    ["Crunchy Murukulu", "మురుకులు", "crunchy-murukulu", "telangana-foods", 140, "500g", "sakinalu", None, None],
    ["Pappu Chekkalu", "పప్పు చెక్కలు", "pappu-chekkalu", "telangana-foods", 145, "500g", "sakinalu", None, None],
    ["Traditional Kudumulu", "కుడుములు", "traditional-kudumulu", "telangana-foods", 100, "500g", "sarvapindi", None, None],
    ["Spicy Boondi", "కారం బూంది", "spicy-boondi", "telangana-foods", 100, "250g", "sakinalu", None, None],
    ["Village Karapusa", "కారపూస", "village-karapusa", "telangana-foods", 110, "500g", "sakinalu", None, None],
    ["Jaggery Ariselu", "అరిసెలు", "jaggery-ariselu", "telangana-foods", 180, "500g", "sarvapindi", "FAMILY RECIPE", None],
    ["Sweet Bobbatlu", "బొబ్బట్లు", "sweet-bobbatlu", "telangana-foods", 160, "500g", "sarvapindi", None, None],
    ["Hand-pressed Janthikalu", "జంతికలు", "hand-pressed-janthikalu", "telangana-foods", 150, "500g", "sakinalu", None, None],
    ["Premium Almonds", "బాదం", "premium-almonds", "dry-fruits", 249, "250g", "almonds", "NATURALLY GOOD", 299],
    ["Whole Cashews", "జీడిపప్పు", "whole-cashews", "dry-fruits", 279, "250g", "almonds", None, None],
    ["Roasted Pistachios", "పిస్తా", "roasted-pistachios", "dry-fruits", 349, "250g", "almonds", None, None],
    ["Premium Walnuts", "వాల్‌నట్స్", "premium-walnuts", "dry-fruits", 299, "250g", "almonds", None, None],
    ["Golden Raisins", "ఎండు ద్రాక్ష", "golden-raisins", "dry-fruits", 119, "250g", "almonds", None, None],
    ["Soft Natural Dates", "ఖర్జూరం", "natural-dates", "dry-fruits", 149, "250g", "almonds", None, None],
    ["Dried Figs", "అంజీర", "dried-figs", "dry-fruits", 329, "250g", "almonds", None, None],
    ["Dried Apricots", "ఎండు ఆప్రికాట్లు", "dried-apricots", "dry-fruits", 259, "250g", "almonds", None, None],
    ["Raw Pumpkin Seeds", "గుమ్మడి గింజలు", "raw-pumpkin-seeds", "seeds", 169, "250g", "seeds", "NUTRIENT RICH", 199],
    ["Sunflower Seeds", "పొద్దుతిరుగుడు గింజలు", "sunflower-seeds", "seeds", 119, "250g", "seeds", None, None],
    ["Chia Seeds", "చియా గింజలు", "chia-seeds", "seeds", 159, "250g", "seeds", None, None],
    ["Natural Flax Seeds", "అవిసె గింజలు", "natural-flax-seeds", "seeds", 89, "250g", "seeds", None, None],
    ["White Sesame Seeds", "నువ్వులు", "white-sesame-seeds", "seeds", 99, "250g", "seeds", None, None],
    ["Watermelon Seeds", "పుచ్చకాయ గింజలు", "watermelon-seeds", "seeds", 159, "250g", "seeds", None, None],
    ["Homemade Gongura Pickle", "గోంగూర పచ్చడి", "homemade-gongura-pickle", "pickles", 149, "250g", "pickle", "TELANGANA SPECIAL", None],
    ["Traditional Avakaya", "ఆవకాయ", "traditional-avakaya", "pickles", 159, "250g", "pickle", None, None],
    ["Village Lemon Pickle", "నిమ్మకాయ పచ్చడి", "village-lemon-pickle", "pickles", 129, "250g", "pickle", None, None],
    ["Farm Vegetable Basket", "తాజా కూరగాయల బుట్ట", "farm-vegetable-basket", "farm-produce", 199, "2kg", "vegetables", "PICKED TODAY", 249],
    ["Fresh Groundnuts", "వేరుశెనగలు", "fresh-groundnuts", "farm-produce", 95, "500g", "grains", None, None],
    ["Raw Village Honey", "సహజ తేనె", "raw-village-honey", "farm-produce", 299, "500g", "ghee", None, None],
    ["Telangana Breakfast Combo", "తెలంగాణ అల్పాహార కాంబో", "telangana-breakfast-combo", "combos", 399, "2kg", "sarvapindi", "SAVE 20%", 499],
    ["Village Snacks Combo", "పల్లె చిరుతిళ్ల కాంబో", "village-snacks-combo", "combos", 449, "2kg", "sakinalu", "SAVE 18%", 549],
    ["Healthy Seeds Combo", "ఆరోగ్య గింజల కాంబో", "healthy-seeds-combo", "combos", 379, "1kg", "seeds", "SAVE 22%", 489],
]

DESCRIPTIONS = {
    "dairy": "Collected fresh each morning from our trusted local farms. Made with care, without unnecessary additives, and brought to your family with the goodness of our village.",
    "telangana-foods": "Handmade in small batches by our village kitchens using time-honoured Telangana family recipes. Authentic ingredients, a familiar taste, and a little love in every bite.",
    "grains": "Naturally grown on Telangana’s fertile soil and carefully cleaned by our farming collective. Honest, wholesome native grains for your everyday family meals.",
    "dry-fruits": "Carefully selected, naturally delicious dry fruits. Packed in small batches for freshness — a wholesome addition to breakfast, homemade sweets, or an afternoon snack.",
    "seeds": "Clean, naturally nutritious seeds, carefully selected and packed for freshness. Add a spoonful to your everyday meals, smoothies, and homemade breads.",
    "farm-produce": "Thoughtfully sourced from our local farmer community. Seasonal goodness with a short journey from the farm to your family’s table.",
    "pickles": "Traditional homemade pickle prepared with fresh ingredients, cold-pressed oil, and our family’s secret spice blend. A taste of Telangana in every spoonful.",
    "combos": "A lovingly curated basket of our village favourites, at a friendlier price. Perfect for sharing the familiar flavours of Telangana with your family.",
}

INGREDIENTS_MAP = {
    "dairy": ["Fresh farm milk"],
    "telangana-foods": ["Rice flour", "Sesame", "Groundnuts", "Curry leaves", "Traditional spices", "Cold-pressed oil"],
    "grains": ["100% native grains"],
    "dry-fruits": ["100% natural dry fruits"],
    "seeds": ["100% natural seeds"],
    "farm-produce": ["Fresh seasonal produce"],
    "pickles": ["Fresh gongura or seasonal fruit", "Cold-pressed sesame oil", "Red chillies", "Salt", "Mustard seeds"],
    "combos": ["Jowar flour", "Ragi flour", "Traditional village favourites"],
}


def ensure_seed_data():
    if Product.objects.exists():
        return

    # 1. Categories
    for c in CATEGORIES_DATA:
        Category.objects.get_or_create(
            slug=c["slug"],
            defaults={
                "name": c["name"],
                "telugu_name": c["telugu_name"],
                "description": c["description"],
                "image": c["image"],
                "icon": c["icon"],
            },
        )

    # 2. Products
    products_list = []
    for index, row in enumerate(ROWS):
        name, telugu_name, slug, cat_slug, price, weight, img, badge, orig_price = row
        cat = Category.objects.get(slug=cat_slug)

        if cat_slug == "dairy" and ("Milk" in name or "Buttermilk" in name):
            weights = ["500ml", "1L", "2L"]
        elif cat_slug == "grains":
            weights = ["1kg", "2kg", "5kg"]
        elif cat_slug == "combos":
            weights = [weight]
        elif cat_slug == "farm-produce":
            weights = [weight, "5kg"]
        else:
            weights = ["250g", "500g", "1kg"]

        stock = 0 if index == 23 else (6 if index in (20, 31) else 35 + (index * 7) % 70)
        farmer = "Ramesh Anna" if cat_slug == "dairy" else ("Lakshmi Amma" if cat_slug in ("telangana-foods", "pickles") else "Srinivas Reddy")
        village = "Siddipet, Telangana" if cat_slug == "dairy" else ("Warangal, Telangana" if cat_slug in ("telangana-foods", "pickles") else "Karimnagar, Telangana")

        desc = (
            "Traditional Telangana rice-flour snack prepared with sesame, groundnuts, fresh herbs, and authentic spices. Hand-patted and slow-cooked in our village kitchen — crispy on the outside, soft in the middle, just like at home."
            if slug == "telangana-sarvapindi"
            else DESCRIPTIONS.get(cat_slug, "")
        )

        p = Product.objects.create(
            id=f"FB-P{str(index + 1).zfill(3)}",
            slug=slug,
            name=name,
            telugu_name=telugu_name,
            description=desc,
            telugu_description="మన ఊరి సహజమైన పదార్థాలతో, సంప్రదాయ పద్ధతుల్లో తయారు చేసిన తాజా ఉత్పత్తి. మీ కుటుంబానికి ప్రేమతో అందిస్తున్నాం.",
            category=cat,
            price=price,
            original_price=orig_price,
            weight=weight,
            weights=weights,
            image=f"/images/{img}.jpg",
            stock=stock,
            farmer=farmer,
            village=village,
            ingredients=INGREDIENTS_MAP.get(cat_slug, []),
            rating=f"{4.6 + (index % 4) / 10:.1f}",
            reviews=28 + (index * 13) % 110,
            badge=badge,
            is_featured=(index < 4 or index in [10, 28, 36, 42, 45]),
            is_organic=True,
        )
        products_list.append(p)

    # 3. Users
    admin_pwd = hash_pwd("FarmBuddy@2026")
    user_pwd = hash_pwd("Village@2026")

    admin_user, _ = UserAccount.objects.get_or_create(
        id="demo-admin",
        defaults={
            "name": "FarmBuddy Admin",
            "email": "admin@farmbuddy.in",
            "phone": "9000010001",
            "password": admin_pwd,
            "role": "admin",
            "addresses": [],
        },
    )

    c1, _ = UserAccount.objects.get_or_create(
        id="demo-customer",
        defaults={
            "name": "Ananya Reddy",
            "email": "customer@farmbuddy.in",
            "phone": "9876543210",
            "password": user_pwd,
            "role": "customer",
            "addresses": [
                {
                    "house": "12-4",
                    "street": "Green Park Road",
                    "area": "Kondapur",
                    "city": "Hyderabad",
                    "district": "Rangareddy",
                    "state": "Telangana",
                    "pincode": "500084",
                }
            ],
        },
    )

    c2, _ = UserAccount.objects.get_or_create(
        id="demo-customer-2",
        defaults={
            "name": "Praveen Kumar",
            "email": "praveen@example.com",
            "phone": "9849012345",
            "password": user_pwd,
            "role": "customer",
        },
    )

    c3, _ = UserAccount.objects.get_or_create(
        id="demo-customer-3",
        defaults={
            "name": "Sowmya Rao",
            "email": "sowmya@example.com",
            "phone": "9700012345",
            "password": user_pwd,
            "role": "customer",
        },
    )

    # 4. Demo Orders
    statuses = ["Delivered", "Delivered", "Delivered", "Delivered", "Packed", "Out for Delivery", "Processing", "Confirmed"]
    now = timezone.now()
    for i in range(16):
        uid = "demo-customer-2" if i % 3 == 0 else ("demo-customer-3" if i % 3 == 1 else "demo-customer")
        u = c2 if i % 3 == 0 else (c3 if i % 3 == 1 else c1)
        p1 = products_list[i % 4]
        p2 = products_list[(10 + i % 8) % len(products_list)]

        items = [
            {
                "productId": p1.id,
                "name": p1.name,
                "teluguName": p1.telugu_name,
                "image": p1.image,
                "weight": p1.weight,
                "quantity": 1 + i % 2,
                "price": p1.price,
            },
            {
                "productId": p2.id,
                "name": p2.name,
                "teluguName": p2.telugu_name,
                "image": p2.image,
                "weight": p2.weight,
                "quantity": 1,
                "price": p2.price,
            },
        ]
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        delivery_fee = 0 if subtotal >= 499 else 40
        total = subtotal + delivery_fee
        order_status = statuses[i % len(statuses)]
        payment_status = "paid" if i < 10 else "pending"

        Order.objects.create(
            id=f"FB-DEMO-{str(i + 1).zfill(4)}",
            owner=uid,
            user=u,
            customer_name=u.name,
            email=u.email,
            phone=u.phone or "9876543210",
            items=items,
            shipping_address={
                "house": "12-4",
                "street": "Green Park Road",
                "area": "Kondapur",
                "city": "Hyderabad",
                "district": "Rangareddy",
                "state": "Telangana",
                "pincode": "500084",
            },
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=0,
            total=total,
            payment_method="Cash on Delivery",
            payment_status=payment_status,
            order_status=order_status,
        )
