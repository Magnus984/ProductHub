from django.db import models
from django.core.cache import cache

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='uploads/products/')
    stock = models.PositiveIntegerField(default=0)
    max_quantity_per_order = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    

    class Meta:
        db_table = 'product'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'product_{self.id}')


    @classmethod
    def get_cached(cls, product_id):
        cache_key = f'product_{product_id}'
        product = cache.get(cache_key)
        if not product:
            product = cls.objects.get(id=product_id)
            cache.set(cache_key, product, timeout=3600)
        return product
    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    product_id = models.ManyToManyField(
        Product,
        related_name="categories"
        )
    
    class Meta:
        db_table = 'category'
    
    

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
        )

    class Meta:
        db_table = 'review'