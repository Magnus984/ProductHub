# admin.py in your orders app
from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'total', 'order_date']
    list_filter = ['status', 'currency']
    search_fields = ['customer__username', 'id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_purchase']
    search_fields = ['product__name', 'order__id']
