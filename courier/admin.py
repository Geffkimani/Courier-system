from django.contrib import admin
from .models import (
    CustomUser, CustomerProfile, StaffProfile, Branch,
    Parcel, Vehicle, Delivery, LoginHistory, PasswordReset
)
from django.contrib.auth.admin import UserAdmin

#each code is commented to slightly explain

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Fields to display in the user list
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']

    # Fields to show when editing an existing user
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('role',)
        }),
    )

    # Fields to show on the initial "Add user" form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'role',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')


class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'phone')
    search_fields = ('user__username', 'phone')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(StaffProfile, StaffProfileAdmin)
admin.site.register(Branch)
admin.site.register(Parcel)
admin.site.register(Vehicle)
admin.site.register(Delivery)
admin.site.register(LoginHistory)
admin.site.register(PasswordReset)
