# Generated by Django 5.1.4 on 2025-01-10 11:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_initial'),
        ('products', '0006_product_is_active_product_max_quantity_per_order_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'order_status_history',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='original_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_date'], name='order_order_d_858e02_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='order_status_35c31c_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['customer_id'], name='order_custome_8ef3e6_idx'),
        ),
        migrations.AddIndex(
            model_name='orderitem',
            index=models.Index(fields=['order_id'], name='order_item_order_i_808c7d_idx'),
        ),
        migrations.AddIndex(
            model_name='orderitem',
            index=models.Index(fields=['product_id'], name='order_item_product_7e833b_idx'),
        ),
        migrations.AddField(
            model_name='orderstatushistory',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='orders.order'),
        ),
    ]