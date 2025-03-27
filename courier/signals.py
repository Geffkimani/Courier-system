from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser, CustomerProfile, StaffProfile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == CustomUser.CUSTOMER:
            CustomerProfile.objects.get_or_create(user=instance)
        elif instance.role == CustomUser.STAFF:
            StaffProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    if instance.role == CustomUser.CUSTOMER:
        try:
            instance.customerprofile.save()
        except CustomerProfile.DoesNotExist:
            pass  # Handle the absence of the profile as needed
    elif instance.role == CustomUser.STAFF:
        try:
            instance.staff_profile.save()
        except StaffProfile.DoesNotExist:
            pass  # Handle the absence of the profile as needed

