from django.urls import path
from . import views

urlpatterns = [
    # Cart endpoints
    path('', views.cart_view, name='cart-view'),
    
    # Cart item-specific endpoints
    path('cart/item/<int:item_id>/', views.cart_item_detail, name='cart-item-detail'),
]
