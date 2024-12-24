from django.urls import path
from . import views

urlpatterns = [
    # Order URLs
    path('', views.order_list, name='order-list'),
    path('<int:pk>/', views.order_detail, name='order-detail'),

    # OrderItem URLs
    path('order-items/', views.order_item_list, name='order-item-list'),
    path('order-items/<int:pk>/', views.order_item_detail, name='order-item-detail'),
]
