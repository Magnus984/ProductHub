from django.db import models
#from ..products.models import Product
from products.models import Product
from users.models import Customer

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('GHc', 'GHc'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    order_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders"
        )
    class Meta:
        db_table = 'order'

class OrderItem(models.Model):
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items"
        )
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items"
        )
    class Meta:
        db_table = 'order_item'