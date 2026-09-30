import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images")
os.makedirs(OUT_DIR, exist_ok=True)

ITEMS = [
    {
        "filename": "village-hero.jpg",
        "size": (1200, 800),
        "bg_top": (43, 81, 59),      # Deep forest green
        "bg_bottom": (232, 216, 179), # Golden wheat
        "accent": (181, 108, 78),     # Terracotta
        "title": "FarmBuddy",
        "subtitle": "From our village, with love.",
        "badge": "TELANGANA ORGANIC COLLECTIVE",
        "emoji": "🌾",
    },
    {
        "filename": "milk.jpg",
        "size": (800, 800),
        "bg_top": (52, 95, 75),
        "bg_bottom": (245, 245, 235),
        "accent": (90, 160, 120),
        "title": "Fresh Farm Milk",
        "subtitle": "Collected Fresh Every Morning",
        "badge": "100% PURE & UNADULTERATED",
        "emoji": "🥛",
    },
    {
        "filename": "sarvapindi.jpg",
        "size": (800, 800),
        "bg_top": (120, 65, 40),
        "bg_bottom": (235, 205, 160),
        "accent": (181, 108, 78),
        "title": "Traditional Sarvapindi",
        "subtitle": "Handmade in Village Kitchens",
        "badge": "TELANGANA SPECIAL RECIPE",
        "emoji": "🍳",
    },
    {
        "filename": "ghee.jpg",
        "size": (800, 800),
        "bg_top": (160, 110, 30),
        "bg_bottom": (250, 235, 180),
        "accent": (210, 150, 40),
        "title": "Desi Bilona Ghee",
        "subtitle": "Traditional Earthen Pot Churned",
        "badge": "PURE DESI COW GHEE",
        "emoji": "🧈",
    },
    {
        "filename": "sakinalu.jpg",
        "size": (800, 800),
        "bg_top": (130, 80, 45),
        "bg_bottom": (240, 220, 190),
        "accent": (195, 120, 75),
        "title": "Handmade Sakinalu",
        "subtitle": "Crispy Sesame & Rice Flour Circles",
        "badge": "FESTIVE DELICACY",
        "emoji": "🥨",
    },
    {
        "filename": "grains.jpg",
        "size": (800, 800),
        "bg_top": (95, 80, 45),
        "bg_bottom": (230, 215, 175),
        "accent": (185, 150, 80),
        "title": "Native Grains & Flours",
        "subtitle": "Jowar, Bajra, Ragi & Telangana Sona",
        "badge": "STONE-GROUND & CHEMICAL FREE",
        "emoji": "🌾",
    },
    {
        "filename": "almonds.jpg",
        "size": (800, 800),
        "bg_top": (100, 60, 40),
        "bg_bottom": (235, 210, 180),
        "accent": (170, 105, 70),
        "title": "Premium Dry Fruits",
        "subtitle": "Almonds, Cashews, Figs & Dates",
        "badge": "100% NATURALLY GOOD",
        "emoji": "🥜",
    },
    {
        "filename": "seeds.jpg",
        "size": (800, 800),
        "bg_top": (50, 85, 60),
        "bg_bottom": (220, 235, 210),
        "accent": (90, 145, 105),
        "title": "Nutrient-Rich Seeds",
        "subtitle": "Chia, Flax, Pumpkin & Sesame Seeds",
        "badge": "ORGANIC SUPERFOODS",
        "emoji": "🌱",
    },
    {
        "filename": "pickle.jpg",
        "size": (800, 800),
        "bg_top": (145, 45, 30),
        "bg_bottom": (245, 205, 175),
        "accent": (200, 70, 45),
        "title": "Village Pickles",
        "subtitle": "Gongura, Avakaya & Village Lemon",
        "badge": "COLD-PRESSED OIL & HAND-GROUND SPICES",
        "emoji": "🫙",
    },
    {
        "filename": "vegetables.jpg",
        "size": (800, 800),
        "bg_top": (45, 90, 50),
        "bg_bottom": (220, 240, 200),
        "accent": (80, 155, 75),
        "title": "Farm Fresh Produce",
        "subtitle": "Harvested Daily with Care",
        "badge": "DIRECT FROM LOCAL FARMS",
        "emoji": "🥬",
    },
    {
        "filename": "farmer-ramesh.jpg",
        "size": (600, 600),
        "bg_top": (40, 80, 65),
        "bg_bottom": (210, 230, 215),
        "accent": (80, 140, 110),
        "title": "Ramesh Anna",
        "subtitle": "Dairy Farmer · Siddipet",
        "badge": "FARMER PARTNER",
        "emoji": "🧑‍🌾",
    },
    {
        "filename": "farmer-lakshmi.jpg",
        "size": (600, 600),
        "bg_top": (125, 55, 45),
        "bg_bottom": (240, 215, 200),
        "accent": (185, 95, 75),
        "title": "Lakshmi Amma",
        "subtitle": "Village Kitchen · Warangal",
        "badge": "TRADITIONAL ARTISAN",
        "emoji": "👩‍🍳",
    },
    {
        "filename": "farmer-srinivas.jpg",
        "size": (600, 600),
        "bg_top": (80, 95, 45),
        "bg_bottom": (225, 235, 195),
        "accent": (145, 165, 80),
        "title": "Srinivas Reddy",
        "subtitle": "Native Grains · Karimnagar",
        "badge": "NATURAL FARMER",
        "emoji": "🌾",
    },
]


def create_gradient_image(info):
    w, h = info["size"]
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    r1, g1, b1 = info["bg_top"]
    r2, g2, b2 = info["bg_bottom"]

    # Smooth vertical gradient
    for y in range(h):
        ratio = y / float(h)
        # Add smooth curve
        t = math.sin(ratio * math.pi / 2)
        r = int(r1 * (1 - t) + r2 * t)
        g = int(g1 * (1 - t) + g2 * t)
        b = int(b1 * (1 - t) + b2 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Decorative concentric circles / organic arches
    center_x = w // 2
    center_y = int(h * 0.45)
    for radius in range(int(min(w, h) * 0.55), 40, -45):
        alpha_color = (
            int(r1 * 0.8 + 255 * 0.2),
            int(g1 * 0.8 + 255 * 0.2),
            int(b1 * 0.8 + 255 * 0.2),
        )
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=alpha_color,
            width=2,
        )

    # Decorative inner card
    card_margin_x = int(w * 0.08)
    card_margin_y = int(h * 0.12)
    card_rect = [card_margin_x, card_margin_y, w - card_margin_x, h - card_margin_y]
    draw.rounded_rectangle(
        card_rect,
        radius=16,
        outline=(255, 255, 255),
        width=3,
    )

    # Accent badge pill
    badge_text = info["badge"]
    badge_w = len(badge_text) * 9 + 30
    badge_h = 32
    bx0 = (w - badge_w) // 2
    by0 = int(h * 0.22)
    draw.rounded_rectangle(
        [bx0, by0, bx0 + badge_w, by0 + badge_h],
        radius=16,
        fill=info["accent"],
    )
    draw.text((bx0 + 15, by0 + 8), badge_text, fill=(255, 255, 255))

    # Center title
    title_text = info["title"]
    subtitle_text = info["subtitle"]

    # Simple text drawing
    draw.text((w // 2 - len(title_text) * 7, int(h * 0.52)), title_text, fill=(35, 55, 40))
    draw.text((w // 2 - len(subtitle_text) * 4, int(h * 0.62)), subtitle_text, fill=(65, 80, 60))

    # Save JPEG
    dest = os.path.join(OUT_DIR, info["filename"])
    img.save(dest, "JPEG", quality=90)
    print(f"Generated: {dest}")


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    for item in ITEMS:
        dest = os.path.join(OUT_DIR, item["filename"])
        if os.path.exists(dest) and not force:
            print(f"Skipping existing image (use --force to overwrite): {dest}")
            continue
        create_gradient_image(item)
    print("Image generation complete.")
