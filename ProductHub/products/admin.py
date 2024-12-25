# admin.py

from django.contrib import admin
from .models import Product, Category
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')  # Include the image field here
    search_fields = ('name', 'category__name')
    list_filter = ('category',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)