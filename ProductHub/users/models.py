from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)  # Use email as login field
    role = models.CharField(max_length=10, choices=ROLES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Fields required when creating a superuser

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username
