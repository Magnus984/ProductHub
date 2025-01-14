from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Order, OrderItem
from products.models import Product, Category
from users.models import Customer, Admin
from django.contrib.auth import get_user_model
from cart.models import Cart, CartItem

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='testpassword', is_customer=True)
        self.user2 = User.objects.create_user(username='testadmin', password='testadminpassword', is_admin=True)
        self.customer = Customer.objects.create(user=self.user1)
        self.admin = Admin.objects.create(user=self.user2)
        self.product = Product.objects.create(
            name='Product_0',
            description="Test Product",
            price=10.0,
            stock=10,
            max_quantity_per_order=2
            )
        self.order1 = Order.objects.create(
            customer_id=self.user1.customer,
            total=30.0,
            original_total=30.0,
            discount_amount=5.0,
            currency='USD',
            status='pending',
        )
        self.order2 = Order.objects.create(
            customer_id=self.user1.customer,
            total=50.0,
            original_total=50.0,
            discount_amount=10.0,
            currency='USD',
            status='processing',
        )

    def test_create_order_without_cart(self):
        """Test creating a new order without cart"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('order-list-create')
        data = {
            'currency': 'USD',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "No cart found. Please create a cart first."})

    def test_create_order_with_empty_cart(self):
        """Test creating order with empty cart"""
        self.client.force_authenticate(user=self.user1)
        self.cart = Cart.objects.create(customer_id=self.user1.customer)
        url = reverse('order-list-create')
        data = {
            'currency': 'USD'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Your cart is empty. Please add items before creating an order."})

    def test_create_order(self):
        """Test creating order when conditions are valid"""
        self.client.force_authenticate(user=self.user1)
        self.cart = Cart.objects.create(customer_id=self.user1.customer)    
        self.item = CartItem.objects.create(cart_id=self.cart, product_id=self.product, quantity=2)
        self.item.save()
        url = reverse('order-list-create')
        data = {
            'currency': 'USD'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_get_all_orders(self):
        self.client.force_authenticate(user=self.user1)
        """Test retrieving all orders for the authenticated customer"""
        url = reverse('order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertGreater(len(response.data['items']), 0)
    


    def test_get_order_detail(self):
        self.client.force_authenticate(user=self.user1)
        """Test retrieving a specific order"""
        url = reverse('order-detail', args=[self.order1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1.id)
        self.assertEqual(response.data['status'], self.order1.status)


    def test_update_order_status(self):
        """Test updating the status of an order"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('order-detail', args=[self.order1.id])
        data = {
            'status': 'processing'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'processing')


    def test_get_order_items(self):
        """Test retrieving all items for a specific order"""
        self.client.force_authenticate(user=self.user1)
        self.orderitem1 = OrderItem(quantity=1, price=10.0, order_id=self.order1, product_id=self.product)
        self.orderitem1.save()
        self.orderitem2 = OrderItem(quantity=2, price=10.0, order_id=self.order1, product_id=self.product)
        self.orderitem2.save()
        url = reverse('order-items', args=[self.order1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
