from rest_framework import serializers
from .models import Cart, CartItem

from products.serializers import ProductSerializer
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Product.objects.all())
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.quantity * obj.product_id.price
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'total_amount', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_total_amount(self, obj):
        return sum(item.quantity * item.product_id.price for item in obj.cart_items.all())

    def get_items_count(self, obj):
        return sum(item.quantity for item in obj.cart_items.all())
