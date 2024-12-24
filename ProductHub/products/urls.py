from django.urls import path
from . import views

urlpatterns = [
    # Product URLs
    path('products/', views.product_list, name='product-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),

    # Category URLs
    path('categories/', views.category_list, name='category-list'),
    path('categories/<int:pk>/', views.category_detail, name='category-detail'),

    # Review URLs
    path('reviews/', views.review_list, name='review-list'),
    path('reviews/<int:pk>/', views.review_detail, name='review-detail'),]
