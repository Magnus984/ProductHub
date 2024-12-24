from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

# Cart Views
@api_view(['GET', 'POST'])
def cart_list(request):
    """
    List all carts or create a new cart for a customer.
    """
    if request.method == 'GET':
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def cart_detail(request, pk):
    """
    Retrieve, update, or delete a specific cart.
    """
    try:
        cart = Cart.objects.get(pk=pk)
    except Cart.DoesNotExist:
        return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CartItem Views
@api_view(['GET', 'POST'])
def cart_item_list(request, cart_id):
    """
    List all items in a cart or create a new cart item.
    """
    if request.method == 'GET':
        cart_items = CartItem.objects.filter(cart_id=cart_id)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        data['cart_id'] = cart_id
        serializer = CartItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def cart_item_detail(request, cart_id, pk):
    """
    Update or delete a specific cart item.
    """
    try:
        cart_item = CartItem.objects.get(pk=pk, cart_id=cart_id)
    except CartItem.DoesNotExist:
        return Response({'detail': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CartItemSerializer(cart_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
