from django.contrib import admin
from .models import Product, Category, Review

# ProductAdmin configuration
class ProductAdmin(admin.ModelAdmin):
    # Display fields in the admin list view
    list_display = ('name', 'price', 'description')

    # Specify fields for the product add/edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price'),
        }),
    )

# Register models
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Review)
