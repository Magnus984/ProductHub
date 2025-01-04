from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's cart or create if doesn't exist"""
        cart, created = Cart.objects.get_or_create(
            customer_id=request.user.customer
        )
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(
            customer_id=request.user.customer
        )

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart,
                product_id=product_id
            )
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart_id=cart,
                product_id_id=product_id,
                quantity=quantity
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def put(self, request, item_id):
        """Update cart item quantity"""
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart_id__customer_id=request.user.customer
            )
            quantity = int(request.data.get('quantity', 1))

            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()

            serializer = CartSerializer(cart_item.cart_id)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, item_id):
        """Remove item from cart"""
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart_id__customer_id=request.user.customer
            )
            cart = cart_item.cart_id
            cart_item.delete()

            serializer = CartSerializer(cart)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Clear all items from cart"""
        cart = Cart.objects.get(customer_id=request.user.customer)
        cart.cart_items.all().delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)