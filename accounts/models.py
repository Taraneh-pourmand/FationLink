from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
        ROLE_CHOICES = [("supplier", "Supplier"), ("wholesale_buyer", "WholeSale_Buyer"), ("admin", "Admin"), ("customer", "Customer")]
        role = models.CharField(max_length=20, choices=ROLE_CHOICES)
