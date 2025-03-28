# Generated by Django 5.1.7 on 2025-03-20 04:51

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courier', '0005_alter_parcel_tracking_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parcel',
            name='delivery_date',
        ),
        migrations.RemoveField(
            model_name='parcel',
            name='pickup_date',
        ),
        migrations.RemoveField(
            model_name='parcel',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='parcel',
            name='sender',
        ),
        migrations.AddField(
            model_name='parcel',
            name='payment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parcel',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('mpesa', 'M-Pesa'), ('paypal', 'PayPal'), ('airtelmoney', 'Airtel Money'), ('card', 'Credit/Debit Card')], max_length=20),
        ),
        migrations.AddField(
            model_name='parcel',
            name='payment_status',
            field=models.CharField(default='Unpaid', max_length=20),
        ),
        migrations.AddField(
            model_name='parcel',
            name='sent_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 3, 20, 4, 51, 44, 139482, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='branch_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels_from', to='courier.branch'),
        ),
        migrations.AlterField(
            model_name='parcel',
            name='branch_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels_to', to='courier.branch'),
        ),
        migrations.AlterField(
            model_name='parcel',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
