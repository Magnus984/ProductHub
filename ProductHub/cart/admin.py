from django.contrib import admin

from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'created_at', 'updated_at')
    search_fields = ('customer_id__user__username',)
    list_filter = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_id', 'product_id', 'quantity', 'created_at', 'updated_at')
    search_fields = ('cart_id__id', 'product_id__name')
    list_filter = ('created_at', 'updated_at')