from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .exceptions import CartItemNotFoundException
from .utils import handle_cart_exceptions, validate_cart_item_quantity, validate_product
from users.permissions import IsCustomer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CartView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Get user's cart or create if doesn't exist",
        tags=['Cart']
    )
    @handle_cart_exceptions
    def get(self, request):
        """Get user's cart or create if doesn't exist"""
        cart, created = Cart.objects.get_or_create(
            customer_id=request.user.customer
        )
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddCartItemView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Add item to cart",
        tags=['Cart'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity', default=1)
            }
        )
    )
    @handle_cart_exceptions
    @transaction.atomic
    def post(self, request):
        """Add item to cart"""

        product_id = request.data.get('product_id')
        product = validate_product(product_id)
        
        quantity = validate_cart_item_quantity(request.data.get('quantity', 1))
        
        cart, created = Cart.objects.get_or_create(
            customer_id=request.user.customer
        )

        cart_item = CartItem.objects.filter(
            cart_id=cart,
            product_id=product.id
        ).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            CartItem.objects.create(
                cart_id=cart,
                product_id=product,
                quantity=quantity
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Update cart item quantity",
        tags=['Cart'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity')
            }
        )
    )
    @handle_cart_exceptions
    @transaction.atomic
    def put(self, request, item_id):
        """Update cart item quantity"""
        quantity = validate_cart_item_quantity(request.data.get('quantity'))
        
        cart_item = CartItem.objects.filter(
            id=item_id,
            cart_id__customer_id=request.user.customer
        ).first()

        if not cart_item:
            raise CartItemNotFoundException()

        validate_product(cart_item.product_id.id)

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart_item.cart_id)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Remove item from cart",
        tags=['Cart']
    )
    @handle_cart_exceptions
    @transaction.atomic
    def delete(self, request, item_id):
        """Remove item from cart"""
        cart_item = CartItem.objects.filter(
            id=item_id,
            cart_id__customer_id=request.user.customer
        ).first()
        
        if not cart_item:
            raise CartItemNotFoundException()

        cart = cart_item.cart_id
        cart_item.delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Clear all items from cart",
        tags=['Cart']
    )
    @handle_cart_exceptions
    @transaction.atomic
    def post(self, request):
        """Clear all items from cart"""
        cart = Cart.objects.get(customer_id=request.user.customer)
        cart.cart_items.all().delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)