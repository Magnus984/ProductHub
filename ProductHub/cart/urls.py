from django.urls import path
from . import views

urlpatterns = [
    # Cart URLs
    path('carts/', views.cart_list, name='cart-list'),
    path('carts/<int:pk>/', views.cart_detail, name='cart-detail'),

    # CartItem URLs
    path('carts/<int:cart_id>/items/', views.cart_item_list, name='cart-item-list'),
    path('carts/<int:cart_id>/items/<int:pk>/', views.cart_item_detail, name='cart-item-detail'),
]
