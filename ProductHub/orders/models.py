from django.db import models
from products.models import Product
from users.models import User

# Order model
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
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    class Meta:
        db_table = 'order'

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

    def calculate_total(self):
        self.total = sum(item.total_price() for item in self.order_items.all())
        self.save()

# OrderItem model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_item'

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.quantity * self.price_at_purchase
