from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from products.models import Product, Category, Review
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from users.models import Customer, Admin

User = get_user_model()

class ProductTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser',
            password='testpassword',
            is_customer=True
        )
        self.customer = Customer.objects.create(user=self.user1)
        self.user2 = User.objects.create_user(
            username='testadmin',
            password='testadminpassword',
            is_admin=True
        )
        self.admin = Admin.objects.create(user=self.user2)
        self.electronics = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
            ) 
        self.laptop = Product.objects.create(
            name='Dell XPS 13',
            description='Dell XPS 13 laptop',
            price=1000.0,
            image='uploads/products/Dell XPS 13 laptop'
            )
        self.laptop.categories.add(self.electronics)
        self.review = Review.objects.create(
            rating=5,
            comment='Great laptop',
            product_id=self.laptop
            )

        self.artwork = Category.objects.create(
            name='Artwork',
            description='Artwork pieces'
            )
        self.poster = Product.objects.create(
            name='The Great Gatsby Poster',
            description='The Great Gatsby Poster',
            price= 20.0,
            image='uploads/products/The_Great_Gatsby_Poster.jpg'
        )
        self.poster.categories.add(self.artwork)

    def tests_get_all_products(self):
        """Test retrieving all products"""
        url = reverse('product-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 2)

    def test_search_products(self):
        """Test searching for products"""
        url = reverse('product-list-create')
        response = self.client.get(url, {'search': 'Dell'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['name'], 'Dell XPS 13')

    def test_filter_products_by_category(self):
        """Test filtering products by category"""
        url = reverse('product-list-create')
        response = self.client.get(url, {'category': self.electronics.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['name'], 'Dell XPS 13')

    def test_filter_products_by_price(self):
        """Test filtering products by price"""
        url = reverse('product-list-create')
        response = self.client.get(url, {'min_price': 10, 'max_price': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['name'], 'The Great Gatsby Poster')

    def test_filter_products_by_rating(self):
        """Test filtering products by rating"""
        url = reverse('product-list-create')
        response = self.client.get(url, {'min_rating': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['name'], 'Dell XPS 13')

    def test_sort_products(self):
        """Test sorting products"""
        url = reverse('product-list-create')
        response = self.client.get(url, {'sort': 'price_asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'][0]['name'], 'The Great Gatsby Poster')


    def test_create_product(self):
        """Test creating a new product"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-list-create')
        image_path = image_path = os.path.join(
            os.path.dirname(__file__),
            '../media/uploads/products/macbook_pro.jpg'
            )
        with open(image_path, 'rb') as image_file:
            image = SimpleUploadedFile(
                name='macbook_pro.jpg',
                content=image_file.read(),
                content_type='image/jpeg'
                )
            data = {
                'name': 'MacBook Pro',
                'description': 'MacBook Pro laptop',
                'price': 1200.0,
                'image': image,
                'categories': [self.electronics.id]
            }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_get_product_detail(self):
        """Test retrieving a specific product"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-detail', args=[self.laptop.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.laptop.id)
        self.assertEqual(response.data['name'], 'Dell XPS 13')

    def test_update_product(self):
        """Test updating a product"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-detail', args=[self.laptop.id])
        image_path = os.path.join(
            os.path.dirname(__file__),
            '../media/uploads/products/dell_xps_15.jpg'
            )
        with open(image_path, 'rb') as image_file:
            image = SimpleUploadedFile(
                name='dell_xps_15.jpg',
                content=image_file.read(),
                content_type='image/jpeg'
            )
            data = {
                'name': 'Dell XPS 15',
                'description': 'Dell XPS 15 laptop',
                'price': 1200.0,
                'image': image,
                'categories': [self.electronics.id]
            }
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.laptop.refresh_from_db()
        self.assertEqual(self.laptop.name, 'Dell XPS 15')
        self.assertEqual(self.laptop.price, 1200.0)

    def test_delete_product(self):
        """Test deleting a product"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-detail', args=[self.laptop.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.laptop.id).exists())

    def test_get_product_reviews(self):
        """Test retrieving reviews for a specific product"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-review', args=[self.laptop.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['items']), 0)
        self.assertEqual(response.data['items'][0]['rating'], self.review.rating)

    def test_add_product_review(self):
        """Test adding a review to a product"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-review', args=[self.laptop.id])
        data = {
            'rating': 4,
            'comment': 'Good laptop'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['comment'], 'Good laptop')
        self.assertEqual(Review.objects.count(), 2)