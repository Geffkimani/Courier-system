# courier/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Parcel

# Signup form for new users (both customers and staff)
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')

# Form for creating a new parcel entry
class ParcelForm(forms.ModelForm):
    class Meta:
        model = Parcel
        fields = ['branch_from', 'branch_to', 'tracking_number', 'description', 'weight', 'dimensions']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
