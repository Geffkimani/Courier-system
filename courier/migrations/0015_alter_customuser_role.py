# Generated by Django 5.1.7 on 2025-03-25 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courier', '0014_alter_customerprofile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('customer', 'Customer'), ('staff', 'Staff'), ('admin', 'Admin')], default='customer', max_length=10),
        ),
    ]
