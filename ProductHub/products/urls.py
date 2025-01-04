# products/urls.py
from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    ProductReviewView,
    CategoryListCreateView,
    CategoryDetailView
)

urlpatterns = [
    # Product URLs
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/reviews/', ProductReviewView.as_view(), name='product-review'),
    
    # Category URLs
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]