from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer

@api_view(['GET', 'POST'])
def cart_view(request):
    """
    Handle viewing and creating a cart.
    - GET: Retrieve the user's cart with items.
    - POST: Add a new item to the cart.
    """
    try:
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # Use session-based cart for unauthenticated users
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)

        if request.method == 'GET':
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)

            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()

            return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['PUT', 'DELETE'])
def cart_item_detail(request, item_id):
    """
    Handle updating and deleting a cart item.
    - PUT: Update the quantity of a cart item.
    - DELETE: Remove a cart item.
    """
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response({'error': 'No active session'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item = CartItem.objects.get(id=item_id, cart__session_key=session_key)

    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        quantity = request.data.get('quantity')

        if quantity is None or int(quantity) <= 0:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)
