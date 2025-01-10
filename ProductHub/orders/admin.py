from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'order_date', 'original_total', 'currency', 'customer_id')
    search_fields = ('status', 'customer_id__user__username')
    list_filter = ('status', 'currency', 'order_date')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'quantity', 'price', 'order_id', 'product_id')
    search_fields = ('order_id__id', 'product_id__name')
    list_filter = ('order_id', 'product_id')