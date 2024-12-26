from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),  # List all orders or create a new order
    path('<int:order_id>/', views.order_detail, name='order_detail'),  # Retrieve, update, or delete a specific order
]
