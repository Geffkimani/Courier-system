#this gives a structure for payment and adding parcel, is a form

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Parcel


class ParcelForm(forms.ModelForm):
    class Meta:
        model = Parcel
        fields = ['branch_from', 'branch_to', 'description', 'weight']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentForm(forms.Form):
    PAYMENT_CHOICES = [
        ('mpesa', 'MPESA'),
        ('airtelmoney', 'Airtel Money'),
        ('paypal', 'PayPal'),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Choose Payment Method"
    )
