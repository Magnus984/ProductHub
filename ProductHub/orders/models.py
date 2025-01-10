from django.db import models
#from ..products.models import Product
from products.models import Product
from users.models import Customer
from decimal import Decimal
from django.db import transaction

class OrderStatusHistory(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes= models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'order_status_history'
        ordering  = ['-timestamp']
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

    VALID_STATUS_TRANSITIONS = {
        'pending': ['processing', 'cancelled'],
        'processing': ['delivered', 'cancelled'],
        'delivered': [],
        'cancelled': [],

    }

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    order_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders"
        )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta:
        db_table = 'order'
        indexes = [
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['customer_id']),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            old_status = Order.objects.get(id=self.pk).status
            if old_status != self.status:
                self._validate_status_transition(old_status, self.status)
                OrderStatusHistory.objects.create(order=self, status=self.status, notes=f"Status changed from {old_status} to {self.status}")
        super().save(*args, **kwargs)
    
    def _validate_status_transition(self, old_status, new_status):
        if new_status not in self.VALID_STATUS_TRANSITIONS[old_status]:
            raise ValueError(f"Invalid status transition from {old_status} to {new_status}")
        
    @classmethod
    def create_from_cart(cls,cart,currency="USD"):
        cart.validate_cart_items()

        total = Decimal(0)
        for item in cart.cart_items.select_related('product_id').all():
            total = item.quantity * item.product_id.price
        
        original_total = total
        discount_amount = Decimal(0)
        final_total = total - discount_amount

        with transaction.atomic():
            order = cls.objects.create(
                customer_id = cart.customer_id,
                total = final_total,
                original_total = original_total,
                discount_amount=discount_amount,
                currency = currency,
                status='pending'
            )

            for cart_item in cart.cart_items.select_related('product_id').all():
                OrderItem.objects.create(
                    order_id = order,
                    product_id = cart_item.product_id,
                    quantity = cart_item.quantity,
                    price = cart_item.product_id.price
                )

                Product.objects.filter(id=cart_item.product_id.id).update(stock=models.F('stock') - cart_item.quantity)

                OrderStatusHistory.objects.create(order=order, status='pending', notes='Order created from cart')
        return order

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
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['product_id']),
        ]

    @property
    def subtotal(self):
        return self.price * self.quantity