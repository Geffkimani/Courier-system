# Generated by Django 5.1.7 on 2025-03-27 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courier', '0019_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='current_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parcel',
            name='current_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
