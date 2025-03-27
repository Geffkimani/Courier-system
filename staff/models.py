from django.contrib.auth.models import User
from django.db import models

from django.conf import settings


class StaffProfile(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    branch = models.ForeignKey('courier.Branch', on_delete=models.SET_NULL, null=True, blank=True,  related_name='staff_staff')

    def __str__(self):
        return self.user.username
