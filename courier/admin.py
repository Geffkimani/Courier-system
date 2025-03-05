# courier/admin.py
from django.contrib import admin
from .models import (
    CustomUser, CustomerProfile, StaffProfile, Branch,
    Parcel, Vehicle, Delivery, LoginHistory
)
from django.contrib.auth.admin import UserAdmin

# Register the custom user model
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomerProfile)
admin.site.register(StaffProfile)
admin.site.register(Branch)
admin.site.register(Parcel)
admin.site.register(Vehicle)
admin.site.register(Delivery)
admin.site.register(LoginHistory)
