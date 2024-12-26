from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from users.serializers import UserSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(source="product_id")

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'price', 'product']

class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(source="customer_id")
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'order_date', 'total', 'currency', 'customer', 'order_items']
