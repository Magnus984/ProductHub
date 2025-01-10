from django.db import models
from users.models import Customer
from products.models import Product
from django.core.exceptions import ValidationError

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="carts"
        )
    class Meta:
        db_table = 'cart'
        
    def validate_cart_items(self):
        """Validate all items in cart for stock and limits"""
        for item in self.cart_items.all():
            product = Product.get_cached(item.product_id.id)
            if not product.is_active:
                raise ValidationError(f"Product {product.name} is no longer available")
            if item.quantity > product.stock:
                raise ValidationError(f"Not enough stock for {product.name}")
            if item.quantity > product.max_quantity_per_order:
                raise ValidationError(f"Maximum quantity exceeded for {product.name}")

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
    class Meta:
        db_table = 'cart_item'