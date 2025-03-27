import base64
import datetime
from django.shortcuts import render
from django.http import HttpResponse
import csv
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import *
from .forms import ParcelForm, PaymentForm
from django.contrib.auth import get_user_model
import logging
import json
from django.http import JsonResponse, HttpResponseBadRequest


logger = logging.getLogger(__name__)

User = get_user_model()



def Home(request):
    return render(request, 'home.html')


# Airtel Money Integration Function (Pseudocode)
def initiate_airtel_money_payment(amount, phone_number, callback_url, transaction_reference):
    api_url = 'https://openapiuat.airtel.africa/'
    headers = {"Authorization": "Bearer YOUR_AIRTEL_ACCESS_TOKEN", "Content-Type": "application/json"}
    payload = {
         "amount": float(amount),
         "phone": phone_number,
         "callback_url": callback_url,
         "transaction_reference": transaction_reference
    }
    response = requests.post(api_url, json=payload, headers=headers)
    try:
        return response.json()
    except ValueError:
        return {'error': 'Invalid JSON response', 'raw': response.text}


def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'login.html')

def LogoutView(request):

    logout(request)

    return redirect('login.html')

def RegisterView(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_data_has_error = False

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists")

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists")

        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, "Password must be at least 5 characters")

        if user_data_has_error:
            return redirect('register')
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            messages.success(request, "Account created. Login now")
            return redirect('login')

    return render(request, 'register.html')


def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'

            email_message = EmailMessage(
                'Reset your password',  # email subject
                email_body,
                settings.EMAIL_HOST_USER,  # email sender
                [email]  # email  receiver
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot_password.html')


def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')


def ResetPassword(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)


    except PasswordReset.DoesNotExist:

        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')


@login_required
def dashboard(request):
    user = request.user

    if user.role == 'customer':
        # Fetch parcels where sender_name matches the user's full name
        parcels = Parcel.objects.filter(sender_name=user.get_full_name())
    elif user.role in ['staff', 'admin']:
        parcels = Parcel.objects.all()
    else:
        parcels = []

    return render(request, 'courier/dashboard.html', {'parcels': parcels})



@login_required
def account_settings(request):
    # Use get_or_create to safely retrieve the profile, creating it only if necessary.
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get form data from POST request
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()

        # Update the profile details
        profile.address = address
        profile.phone = phone
        profile.save()

        messages.success(request, "Your profile has been updated.")
        return redirect('dashboard')  # Redirect as needed

    context = {
        'customer_profile': profile,
    }
    return render(request, 'courier/account_settings.html', context)

@login_required
def add_parcel(request):
    branches = Branch.objects.all()  # Get all available branches

    if request.method == "POST":
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)

            branch_from_id = request.POST.get("branch_from")
            branch_to_id = request.POST.get("branch_to")
            description = request.POST.get("description")
            weight = request.POST.get("weight")

            if not branch_from_id or not branch_to_id or not description or not weight:
                messages.error(request, "All fields are required.")
                return redirect("add_parcel")

            # Convert weight to float
            try:
                weight = float(weight)
            except ValueError:
                messages.error(request, "Invalid weight format.")
                return redirect("add_parcel")

            # Get selected branch instances
            branch_from = Branch.objects.get(id=branch_from_id)
            branch_to = Branch.objects.get(id=branch_to_id)

            # Create the parcel
            parcel = Parcel.objects.create(
                sender_name=customer_profile.user.get_full_name(),
                branch_from=branch_from,
                branch_to=branch_to,
                description=description,
                weight=weight,
                tracking_number=generate_unique_tracking_number(),
                status="Pending"
            )

            return redirect('parcel_confirmation', parcel_id=parcel.id)

        except CustomerProfile.DoesNotExist:
            messages.error(request, "You must have a customer profile to send a parcel.")
            return redirect("dashboard")

        except Branch.DoesNotExist:
            messages.error(request, "Selected branch does not exist.")
            return redirect("add_parcel")

    return render(request, "courier/addparcel.html", {"branches": branches})

@login_required
def parcel_confirmation(request, parcel_id):
    try:
        user_full_name = request.user.get_full_name().strip().lower()
        parcel = Parcel.objects.get(
            id=parcel_id,
            sender_name__iexact=user_full_name
        )
    except Parcel.DoesNotExist:
        return render(request, 'courier/error.html', {'message': 'Parcel not found or does not belong to you.'})

    return render(request, 'courier/parcel_confirmation.html', {'parcel': parcel})

@login_required
def delete_parcel(request, parcel_id):
    parcel = Parcel.objects.get(id=parcel_id)
    if request.user == parcel.sender_name.user:
        parcel.delete()
    messages.success(request, "Parcel deleted successfully.")
    return redirect('dashboard')


@login_required
def payment_page(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Process payment selection here
            pass
    else:
        form = PaymentForm()
    context = {
        'parcel': parcel,
        'form': form,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID
    }
    return render(request, 'courier/payment.html', context)





def update_parcel_location(request):
    # Assume this view is called with POST data containing:
    # tracking_number, latitude, and longitude
    if request.method == "POST":
        data = json.loads(request.body)
        tracking_number = data.get("tracking_number")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        parcel = get_object_or_404(Parcel, tracking_number=tracking_number)

        # Optionally, create a ParcelLocation instance:
        parcel_location = ParcelLocation.objects.create(
            parcel=parcel,
            latitude=latitude,
            longitude=longitude,
            timestamp=timezone.now()
        )

        # Broadcast update via Channels:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"tracking_{tracking_number}",
            {
                "type": "tracking_update",  # This calls the tracking_update() method in our consumer
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": str(parcel_location.timestamp),
            }
        )
        return JsonResponse({"message": "Location updated successfully."})
    return JsonResponse({"error": "Invalid method."}, status=405)


def customer_report(request):
    customer = request.user.customerprofile  # Get the logged-in customer
    parcels = Parcel.objects.filter(receiver=customer)  # Fetch only customer-related parcels

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_parcels_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tracking Number', 'Destination', 'Status', 'Delivery Date'])

    for parcel in parcels:
        writer.writerow([parcel.tracking_number, parcel.branch_to.name, parcel.status, parcel.delivery_date])

    return response