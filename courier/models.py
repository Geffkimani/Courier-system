import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

def get_default_user():
    User = get_user_model()
    return User.objects.first() if User.objects.exists() else None


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    CUSTOMER = 'customer'
    STAFF = 'staff'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (STAFF, 'Staff'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CUSTOMER
    )
    objects = CustomUserManager()

    def __str__(self):
        return self.username



class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customerprofile')
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="staff_profile")
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} (Staff)"

# Branch Model
class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

def generate_unique_tracking_number():
    while True:
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Parcel.objects.filter(tracking_number=tracking_number).exists():
            return tracking_number

class Report(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Parcel(models.Model):
    #sender = models.ForeignKey(CustomerProfile, related_name='sent_parcels', on_delete=models.CASCADE)
    #sender = models.ForeignKey(
        #CustomerProfile, related_name='sent_parcels', on_delete=models.SET_NULL, null=True, blank=True
    #)
    sender_name = models.CharField(max_length=255, default="Unknown Sender")
    receiver = models.ForeignKey(CustomerProfile, related_name='received_parcels', on_delete=models.CASCADE, null=True, blank=True)
    branch_from = models.ForeignKey(Branch, related_name='parcels_sent', on_delete=models.CASCADE)
    branch_to = models.ForeignKey(Branch, related_name='parcels_received', on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=6, unique=True, default=generate_unique_tracking_number, editable=False)
    description = models.TextField(blank=True)
    weight = models.FloatField()
    pickup_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    #created_by_staff = models.ForeignKey(StaffProfile, related_name='registered_parcels', on_delete=models.SET_NULL,
                                         #null=True, blank=True)
    #created_by_staff = models.ForeignKey('staff.StaffProfile', on_delete=models.CASCADE)
    created_by_staff = models.ForeignKey('staff.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.tracking_number

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.license_plate

class Delivery(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    current_location = models.CharField(max_length=255)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='In Transit')

    def __str__(self):
        return f"Delivery for {self.parcel.tracking_number}"

class LoginHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"

class PasswordReset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

