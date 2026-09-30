from django.core.management.base import BaseCommand
from api.seeds import ensure_seed_data
from api.models import Product, Category, UserAccount, Order


class Command(BaseCommand):
    help = "Seeds initial categories, products, admin and customer accounts, and demo orders."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding FarmBuddy database..."))
        ensure_seed_data()
        cat_count = Category.objects.count()
        prod_count = Product.objects.count()
        user_count = UserAccount.objects.count()
        order_count = Order.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded: {cat_count} categories, {prod_count} products, {user_count} users, {order_count} orders."
            )
        )
