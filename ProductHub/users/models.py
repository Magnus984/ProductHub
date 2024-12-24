from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    """Custom user model."""
    residential_address = models.CharField(max_length=80, blank=True, null=True)
    is_customer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


class Customer(models.Model):
    """Customer model."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="customer"
        )

    class Meta:
        db_table = 'customer'


class Admin(models.Model):
    """Admin model."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="admin"
        )

    class Meta:
        db_table = 'admin'
