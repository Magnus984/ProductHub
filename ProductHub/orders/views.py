from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from .serializers import OrderSerializer, OrderItemSerializer
from utils.pagination import CustomPagination
from users.permissions import IsCustomer, IsAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError
from users.models import Customer
import json 
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
from .utils import verify_paystack_payment
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import hmac
import hashlib


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="Get all orders for the authenticated customer",
        tags=['Orders'],
        responses={200: OrderSerializer}
    )
    def get(self, request):
        """Get all orders for the authenticated customer"""
        orders = Order.objects.filter(customer_id=request.user.customer)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(orders,request)
        serializer = OrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new order with order items",
        tags=['Orders'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'currency': openapi.Schema(type=openapi.TYPE_STRING, description='Currency'),
            }
        )
    )
          
    @transaction.atomic
    def post(self, request):
        """Create a new order from the customer's cart"""
        try:
            # Get the customer's most recent cart
            cart = Cart.objects.filter(
                customer_id=request.user.customer
            ).latest('created_at')
            
            # Check if cart has items
            if not cart.cart_items.exists():
                return Response(
                    {"error": "Your cart is empty. Please add items before creating an order."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get currency from request or use default
            currency = request.data.get('currency', 'USD')
            
            # Validate currency choice
            if currency not in dict(Order.CURRENCY_CHOICES):
                return Response(
                    {"error": f"Invalid currency. Choices are: {', '.join(dict(Order.CURRENCY_CHOICES).keys())}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add validate_cart_items method to your Cart model if not exists
            def validate_cart_items(cart):
                for item in cart.cart_items.select_related('product_id').all():
                    if item.product_id.stock < item.quantity:
                        raise ValidationError(
                            f"Insufficient stock for product {item.product_id.name}. "
                            f"Available: {item.product_id.stock}, Requested: {item.quantity}"
                        )
            
            # Validate cart items
            validate_cart_items(cart)
            
            # Create order from cart
            order = Order.create_from_cart(cart, currency=currency)
            
            # Serialize and return the created order
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Cart.DoesNotExist:
            return Response(
                {"error": "No cart found. Please create a cart first."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    
        # # Add customer to the order data
        # order_data = request.data.copy()
        # order_data['customer_id'] = request.user.customer.id
        
        # # Validate and create order
        # order_serializer = OrderSerializer(data=order_data)
        # if not order_serializer.is_valid():
        #     return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # order = order_serializer.save()
        
        # # Process order items
        # order_items = request.data.get('order_items', [])
        # for item in order_items:
        #     item['order_id'] = order.id
        #     item_serializer = OrderItemSerializer(data=item)
        #     if item_serializer.is_valid():
        #         item_serializer.save()
        #     else:
        #         raise serializers.ValidationError(item_serializer.errors)
        
        # # Fetch the complete order with items
        # updated_order = Order.objects.get(id=order.id)
        # result_serializer = OrderSerializer(updated_order)
        
        # return Response(result_serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'PATCH':
            self.permission_classes = [IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsCustomer]
        return super().get_permissions()
    #permission_classes = [IsAuthenticated, IsCustomer]
    @swagger_auto_schema(
        operation_description="Get a specific order",
        tags=['Orders']
    )
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

    @swagger_auto_schema(
        operation_description="Update order status",
        tags=['Orders'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Order status')
            }
        )
    )
    @transaction.atomic
    def patch(self, request, order_id):
        """Update order status"""
        try:
            order = Order.objects.get(id=order_id)
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
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Get all items for a specific order",
        tags=['Orders']
    )
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


class CheckoutOrder(APIView):
    """checks out order"""
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Checks out and order by making payment",
        tags=["Orders"],
    )
    def post(self, request, order_id):
        #getting order using order_id
        order = get_object_or_404(Order, id=order_id)
        customer = Customer.objects.get(id=order.customer_id.id)
        total = int(order.total * 100) #converting to smallest currency unit

        #initializing payment
        url = "https://api.paystack.co/transaction/initialize"

        PAYSTACK_SECRET_KEY = settings.PAYSTACK_LIVE_SECRET_KEY
        print(PAYSTACK_SECRET_KEY)
        data = {
            "email": customer.user.email,
            "amount": total,
        }
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url=url, data=json.dumps(data), headers=headers)
        response_data = response.json()
        print(response_data)
        if response.status_code != 200:
            return Response({"error": "Payment initialization failed"}, status=status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        print(response_data)
        reference = response_data['data']['reference']
        order.reference = reference
        order.save()
        return Response(
            {"message": "Payment initialized", "authorization_url": response_data['data']['authorization_url']},
            status=status.HTTP_200_OK
        )


@csrf_exempt
@api_view(["POST"])
def paystack_webhook(request):
    secret_key = settings.PAYSTACK_LIVE_SECRET_KEY
    payload = request.body
    signature = request.headers.get('X-Paystack-Signature')

    if not signature:
        return Response({"error": "Missing signature header"}, status=400)

    # Verify the signature
    generated_signature = hmac.new(
        bytes(secret_key, 'utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()

    if generated_signature != signature:
        return Response({"error": "Invalid signature"}, status=400)

    # Parse and handle the event
    event = json.loads(payload)
    if event['event'] == 'charge.success':
        data = event['data']
        reference = data['reference']

        # Find the order by reference and update its status
        try:
            order = Order.objects.get(reference=reference)
            if order.status != 'paid':
                order.status = 'paid'
                order.save()
            return Response({"message": "Payment verified"}, status=200)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

    return Response({"message": "Unhandled event"}, status=200)