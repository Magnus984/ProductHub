# Generated by Django 5.1.4 on 2025-01-08 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_review_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.DecimalField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], decimal_places=1, max_digits=2),
        ),
    ]