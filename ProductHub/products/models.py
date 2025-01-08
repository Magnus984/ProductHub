from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='uploads/products/')
    

    class Meta:
        db_table = 'product'


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