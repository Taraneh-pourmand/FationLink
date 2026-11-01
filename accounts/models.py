from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        SELLER = "seller", "Seller"
        WHOLESALER = "wholesaler", "Wholesaler"
        MANUFACTURER = "manufacturer", "Manufacturer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
            return f"{self.username} ({self.get_role_display()})"