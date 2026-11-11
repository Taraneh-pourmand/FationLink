import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Product, Order, OrderItem, Review, SupplierLink

User = get_user_model()

REVIEWS = [
    (5, "Great quality, I love it"),
    (5, "Excellent product, fast delivery"),
    (4, "Good value for the price"),
    (2, "Poor quality, it broke after a week"),
    (1, "Terrible, I want a refund"),
]

class Command(BaseCommand):
    def handle(self, *args, **opts):
        def mk(username, role):
            u, created = User.objects.get_or_create(username=username, defaults={"role": role})
            if created:
                u.set_password("test1234")
                u.save()
            return u

        sellers = [mk("seller1", "seller"), mk("seller2", "seller")]
        wholesaler = mk("wholesaler1", "wholesaler")
        mk("manufacturer1", "manufacturer")
        customers = [mk(f"customer{i}", "customer") for i in range(1, 6)]

        tshirt, _ = Category.objects.get_or_create(name="T-shirt")
        skirt, _ = Category.objects.get_or_create(name="skirt")

        products = []
        for i in range(1, 9):
            p, _ = Product.objects.get_or_create(
                name=f"Product {i}",
                defaults=dict(seller=random.choice(sellers),
                              category=random.choice([tshirt, skirt]),
                              price=Decimal(random.randint(10, 90)),
                              stock=100, description="Sample product"))
            products.append(p)

        if not Order.objects.exists():
            for c in customers:
                for _ in range(4):
                    o = Order.objects.create(buyer=c)
                    for p in random.sample(products, 2):
                        OrderItem.objects.create(order=o, product=p,
                                                 quantity=random.randint(1, 3),
                                                 unit_price=p.price)
                        if not Review.objects.filter(product=p, user=c).exists():
                            r = random.choice(REVIEWS)
                            Review.objects.create(product=p, user=c, rating=r[0], comment=r[1])

        SupplierLink.objects.get_or_create(seller=sellers[0], supplier=wholesaler, defaults={"approved": True})
        SupplierLink.objects.get_or_create(seller=sellers[1], supplier=wholesaler)
        self.stdout.write("Done. Password for all users: test1234")
