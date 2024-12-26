from rest_framework import serializers
from .models import Cart, CartItem

from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items, including product details.
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping cart, including all items.
    """
    items = CartItemSerializer(many=True, read_only=True, source='cartitem_set')
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        """Calculate total price of all items in cart."""
        return sum(item.product.price * item.quantity for item in obj.cartitem_set.all())
