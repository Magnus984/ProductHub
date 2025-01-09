from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from products.models import Product
from .models import CartItem, Cart
from users.models import Customer

User = get_user_model()

class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            is_customer=True
        )
        self.customer = Customer.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            name='Product_0',
            description="Test Product",
            price=10.0
            )
        self.second_product = Product.objects.create(
            name='Product_1',
            description="Test Product",
            price=10.0
            )

    def test_get_cart(self):
        """Test retrieving the user's cart"""
        url = reverse('cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)

    def test_add_to_cart(self):
        """Test adding an item to the cart"""
        url = reverse('cart-items')
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart_items'][0]['id'], self.product.id)
        self.assertEqual(response.data['cart_items'][0]['quantity'], 2)

    def test_update_cart_item(self):
        """Test updating the quantity of an item in the cart"""
        cart = Cart.objects.create(customer_id=self.user.customer)
        cart_item = CartItem.objects.create(cart_id=cart, product_id=self.product, quantity=1)
        url = reverse('cart-item-detail', args=[cart_item.id])
        data = {
            'quantity': 5
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_from_cart(self):
        """Test removing item from the cart"""
        cart = Cart.objects.create(customer_id=self.user.customer)
        cart_item = CartItem.objects.create(cart_id=cart, product_id=self.product, quantity=1)
        url = reverse('cart-item-detail', args=[cart_item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_clear_cart(self):
        """Test clearing the cart"""
        cart = Cart.objects.create(customer_id=self.user.customer)
        CartItem.objects.create(cart_id=cart, product_id=self.product, quantity=1)
        CartItem.objects.create(cart_id=cart, product_id=self.second_product, quantity=2)
        url = reverse('clear-cart')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItem.objects.filter(cart_id=cart).count(), 0)
