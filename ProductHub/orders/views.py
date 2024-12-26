from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from products.models import Product
from users.models import User

@api_view(['GET', 'POST'])
def order_list(request):
    """
    Handle viewing all orders or creating a new order.
    - GET: Retrieve all orders for the authenticated customer.
    - POST: Create a new order with items.
    """
    if request.method == 'GET':
        customer = request.user
        if not isinstance(customer, User):
            return Response({'error': 'Invalid user'}, status=status.HTTP_403_FORBIDDEN)
        
        orders = Order.objects.filter(customer_id=customer)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        customer = request.user
        if not isinstance(customer, User):
            return Response({'error': 'Invalid user'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        order_items_data = data.pop('order_items', [])
        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            order = order_serializer.save(customer_id=customer)
            for item_data in order_items_data:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity', 1)

                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response({'error': f'Product with ID {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)

                OrderItem.objects.create(
                    order_id=order,
                    product_id=product,
                    quantity=quantity,
                    price=product.price
                )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def order_detail(request, order_id):
    """
    Handle retrieving, updating, or deleting a specific order.
    - GET: Retrieve a specific order with items.
    - PUT: Update the order status.
    - DELETE: Delete an order.
    """
    try:
        order = Order.objects.get(id=order_id, customer_id=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        if 'status' in request.data:
            order.status = request.data['status']
            order.save()
            return Response({'message': 'Order status updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        order.delete()
        return Response({'message': 'Order deleted'}, status=status.HTTP_204_NO_CONTENT)
