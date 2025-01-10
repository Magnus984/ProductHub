from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order_id', 'quantity', 'price', 'product_id']
        read_only_fields = ['id', 'order_id', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'order_date', 'total', 'currency', 'customer_id', 'order_items', 'discount_amount', 'original_total']
        read_only_fields = ['id', 'status', 'order_date', 'total', 'customer_id', 'discount_amount', 'original_total']
        extra_kwargs = {
            'currency': {'required': False}
        }