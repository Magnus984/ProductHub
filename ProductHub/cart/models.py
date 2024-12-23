from django.db import models
from users.models import Customer
from products.models import Product

# Create your models here.
class Cart(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="carts"
        )

class CartItem(models.Model):
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart_id = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items"
        )
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
        )