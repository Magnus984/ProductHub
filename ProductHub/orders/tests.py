from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Order, OrderItem
from products.models import Product, Category
from users.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', is_customer=True)
        self.customer = Customer.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        
        self.electronics = Category.objects.create(name='Electronics', description='Electronic devices')
        self.laptop = Product.objects.create(
            name='Dell XPS 13',
            description='Dell XPS 13 laptop',
            price=1000.0,
            image='uploads/products/Dell_XPS_13.jpg'
        )
        self.laptop.categories.add(self.electronics)
        
        self.order = Order.objects.create(
            status='pending',
            total=1000.00,
            currency='USD',
            customer_id=self.customer
        )
        self.order_item = OrderItem.objects.create(
            quantity=1,
            price=1000.00,
            order_id=self.order,
            product_id=self.laptop
        )

    def test_get_all_orders(self):
        """Test retrieving all orders for the authenticated customer"""
        url = reverse('order-list-create')
        response = self.client.get(url)
        print("response data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertGreater(len(response.data['items']), 0)

    def test_create_order(self):
        """Test creating a new order with order items"""
        url = reverse('order-list-create')
        data = {
            'status': 'pending',
            'total': 1200.00,
            'currency': 'USD',
            'order_items': [
                {
                    'quantity': 1,
                    'price': 1200.00,
                    'product_id': self.laptop.id
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(OrderItem.objects.count(), 2)

    def test_get_order_detail(self):
        """Test retrieving a specific order"""
        url = reverse('order-detail', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
        self.assertEqual(response.data['status'], self.order.status)

    def test_update_order_status(self):
        """Test updating the status of an order"""
        url = reverse('order-detail', args=[self.order.id])
        data = {
            'status': 'processing'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')

    def test_get_order_items(self):
        """Test retrieving all items for a specific order"""
        url = reverse('order-items', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        expected_price = f"{self.order_item.price:.2f}"
        response_price = f"{float(response.data[0]['price']):.2f}"
        self.assertEqual(response.data[0]['quantity'], self.order_item.quantity)
        self.assertEqual(response_price, expected_price)
