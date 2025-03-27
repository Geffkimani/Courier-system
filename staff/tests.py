from django.test import TestCase

# Create your tests here.


from staff.models import StaffProfile
from courier.models import CustomUser

user = CustomUser.objects.get(username='philip')
print(StaffProfile.objects.filter(user=user))

staff_profile = StaffProfile.objects.create(user=user, branch=THIKA)

from staff.models import StaffProfile
from courier.models import CustomUser

# Get the existing user
user = CustomUser.objects.get(username='philip')

# Create a StaffProfile for this user (update branch field accordingly)
staff_profile = StaffProfile.objects.create(user=user, branch=some_branch)
staff_profile.save()

print("StaffProfile created:", staff_profile)
