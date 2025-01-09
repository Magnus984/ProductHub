# cart/urls.py
from django.urls import path
from .views import CartView, AddCartItemView, CartItemDetailView, ClearCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('items/', AddCartItemView.as_view(), name='cart-items'),
    path('items/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('clear/', ClearCartView.as_view(), name='clear-cart'),
]