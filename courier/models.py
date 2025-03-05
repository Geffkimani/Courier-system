from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Override the groups field with a unique related_name
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",  # Changed from default 'user_set'
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    # Override the user_permissions field with a unique related_name
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",  # Changed from default 'user_set'
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username

# Additional Models

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} (Staff)"

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Parcel(models.Model):
    sender = models.ForeignKey(CustomerProfile, related_name='sent_parcels', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomerProfile, related_name='received_parcels', on_delete=models.CASCADE, null=True, blank=True)
    branch_from = models.ForeignKey(Branch, related_name='parcels_sent', on_delete=models.CASCADE)
    branch_to = models.ForeignKey(Branch, related_name='parcels_received', on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    dimensions = models.CharField(max_length=50)
    pickup_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')

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
