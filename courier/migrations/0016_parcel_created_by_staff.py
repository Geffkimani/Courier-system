# Generated by Django 5.1.7 on 2025-03-26 05:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courier', '0015_alter_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='created_by_staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registered_parcels', to='courier.staffprofile'),
        ),
    ]
