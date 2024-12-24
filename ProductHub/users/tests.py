from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer(self):
        url = reverse('register-customer')
        data = {
            'username': 'customer1',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'email': 'customer1@example.com',
            'residential_address': '123 Main St, Accra'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='customer1').exists())

    def test_register_admin(self):
        url = reverse('register-admin')
        data = {
            'username': 'admin1',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'password': 'password123',
            'email': 'admin1@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='admin1').exists())
    

    def test_register_customer_existing_username(self):
        User.objects.create_user(username='customer1', password='password123')
        url = reverse('register-customer')
        data = {
            'username': 'customer1',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'email': 'customer1@example.com',
            'residential_address': '123 Main St, Accra'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_customer_existing_email(self):
        User.objects.create_user(username='customer2', email='customer1@example.com', password='password123')
        url = reverse('register-customer')
        data = {
            'username': 'customer1',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'email': 'customer1@example.com',
            'residential_address': '123 Main St, Accra'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_admin_existing_username(self):
        User.objects.create_user(username='admin1', password='password123')
        url = reverse('register-admin')
        data = {
            'username': 'admin1',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'password': 'password123',
            'email': 'admin1@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_admin_existing_email(self):
        User.objects.create_user(username='admin2', email='admin1@example.com', password='password123')
        url = reverse('register-admin')
        data = {
            'username': 'admin1',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'password': 'password123',
            'email': 'admin1@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_user(self):
        user = User.objects.create_user(username='user1', password='password1234')
        url = reverse('login')
        data = {
            'username': 'user1',
            'password': 'password1234'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_user(self):
        user = User.objects.create_user(username='user2', password='password1236')
        self.client.login(username='user2', password='password1236')
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)