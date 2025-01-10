from django.db import models
from django.core.exceptions import ValidationError
from products.models import Product
from users.models import Customer
from decimal import Decimal
from django.db.models import F
from django.utils import timezone
from django.db import transaction

class OrderStatusHistory(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'order_status_history'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.order} - {self.status}"

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
        'cancelled': []
    }

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['customer_id']),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:  # If updating existing order
            old_status = Order.objects.get(pk=self.pk).status
            if old_status != self.status:
                self._validate_status_transition(old_status, self.status)
                # Record status change
                OrderStatusHistory.objects.create(
                    order=self,
                    status=self.status,
                    notes=f"Status changed from {old_status} to {self.status}"
                )
        super().save(*args, **kwargs)

    def _validate_status_transition(self, old_status, new_status):
        """Validate if the status transition is allowed"""
        if new_status not in self.VALID_STATUS_TRANSITIONS[old_status]:
            raise ValidationError(f"Invalid status transition from {old_status} to {new_status}")

    @classmethod
    def create_from_cart(cls, cart, currency='USD'):
        """Create an order from a cart with automatic total calculation"""
        with transaction.atomic():
            # Validate cart items
            cart.validate_cart_items()

            # Calculate total from cart items
            total = Decimal('0')
            for item in cart.cart_items.select_related('product_id').all():
                total += item.quantity * item.product_id.price

            # Store original total before any discounts
            original_total = total

            # Apply any discounts here if needed
            discount_amount = Decimal('0')  # Calculate discount if any
            final_total = total - discount_amount

            # Create the order
            order = cls.objects.create(
                customer_id=cart.customer_id,
                total=final_total,
                original_total=original_total,
                discount_amount=discount_amount,
                currency=currency
            )

            # Create order items and update stock
            for cart_item in cart.cart_items.select_related('product_id').all():
                OrderItem.objects.create(
                    order_id=order,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product_id.price
                )
                # Update stock
                Product.objects.filter(id=cart_item.product_id.id).update(
                    stock=F('stock') - cart_item.quantity
                )

            # Record initial status
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                notes="Order created"
            )

            # Clear the cart after successful order creation
            cart.cart_items.all().delete()

            return order
    def __str__(self):
        return f"Order {self.id} - {self.status}"

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
        """Calculate subtotal for the order item"""
        return self.quantity * self.price