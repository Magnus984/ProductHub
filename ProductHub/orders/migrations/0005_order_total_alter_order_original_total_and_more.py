# Generated by Django 5.1.4 on 2025-01-10 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_order_total_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='original_total',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], max_length=20),
        ),
        migrations.AlterField(
            model_name='orderstatushistory',
            name='notes',
            field=models.TextField(blank=True, default=0),
            preserve_default=False,
        ),
    ]