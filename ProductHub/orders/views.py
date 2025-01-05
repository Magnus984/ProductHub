from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from utils.pagination import CustomPagination



class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        """Get all orders for the authenticated customer"""
        orders = Order.objects.filter(customer_id=request.user.customer)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(orders,request)
        serializer = OrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request):
        """Create a new order with order items"""
        
        # Add customer to the order data
        order_data = request.data.copy()
        order_data['customer_id'] = request.user.customer.id
        
        # Validate and create order
        order_serializer = OrderSerializer(data=order_data)
        if not order_serializer.is_valid():
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        order = order_serializer.save()
        
        # Process order items
        order_items = request.data.get('order_items', [])
        for item in order_items:
            item['order_id'] = order.id
            item_serializer = OrderItemSerializer(data=item)
            if item_serializer.is_valid():
                item_serializer.save()
            else:
                raise serializers.ValidationError(item_serializer.errors)
        
        # Fetch the complete order with items
        updated_order = Order.objects.get(id=order.id)
        result_serializer = OrderSerializer(updated_order)
        
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """Get a specific order"""
        try:
            order = Order.objects.get(id=order_id, customer_id=request.user.customer)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @transaction.atomic
    def patch(self, request, order_id):
        """Update order status"""
        try:
            order = Order.objects.get(id=order_id, customer_id=request.user.customer)
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class OrderItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """Get all items for a specific order"""
        try:
            order = Order.objects.get(id=order_id, customer_id=request.user.customer)
            items = OrderItem.objects.filter(order_id=order)
            serializer = OrderItemSerializer(items, many=True)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )