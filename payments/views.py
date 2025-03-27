from django.shortcuts import render, get_object_or_404, redirect
from paypal.standard.forms import PayPalPaymentsForm

from courier.forms import PaymentForm
from courier.models import Parcel
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.urls import  reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.shortcuts import render
import uuid
from django.contrib.auth.decorators import login_required
from courier.views import initiate_airtel_money_payment
from .utils import get_mpesa_access_token, generate_lipa_na_mpesa_password



@login_required
def proceed_to_payment(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)
    amount = parcel.weight
    phone_number = request.user.customerprofile.phone

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            #This is where we  Build a callback URL for payment providers. !! error on Mpesa API and airtel
            callback_url = request.build_absolute_uri(reverse('payments:mpesa_callback'))
            if payment_method == 'mpesa':
                response = lipa_na_mpesa_online(amount, phone_number, callback_url, "REF123", "Payment for Parcel")
            elif payment_method == 'airtelmoney':
                response = initiate_airtel_money_payment(amount, phone_number, callback_url, "REF123")
            elif payment_method == 'paypal':
                response = {"status": "redirect", "url": "https://www.sandbox.paypal.com/checkoutnow?token=YOUR_TOKEN"}
                return redirect(response["url"])
            else:
                response = {"error": "Invalid payment method selected."}
            # Process the response as needed / store transaction details etc
            return render(request, 'payments/payment_success.html', {
                'parcel': parcel,
                'payment_method': payment_method,
                'payment_response': response
            })
    else:
        form = PaymentForm()
    return render(request, 'payments/payment.html', {'parcel': parcel, 'form': form})


def process_payment(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)

    # Determine the amount to be paid. You could set this based on parcel weight, distance, etc.
    amount = "10.00"  # For example, $10.00

    # PayPal settings
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": amount,
        "item_name": f"Payment for Parcel {parcel.tracking_number}",
        "invoice": str(parcel.id),
        "notify_url": request.build_absolute_uri("/paypal/ipn/"),
        "return_url": request.build_absolute_uri(f"/payments/success/{parcel.id}/"),
        "cancel_return": request.build_absolute_uri(f"/payments/cancel/{parcel.id}/"),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)

    context = {"form": form, "parcel": parcel}
    return render(request, "payments/process_payment.html", context)


def lipa_na_mpesa_online(request):
    """
    Initiates an MPESA STK push transaction.
    - Retrieves an access token.
    - Generates the required password and timestamp.
    - Constructs and sends the API request to initiate the payment.
    Returns the JSON response from MPESA.
    """
    # Retrieve the access token
    access_token = get_mpesa_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Generate the password and timestamp for the transaction
    password, timestamp = generate_lipa_na_mpesa_password()

    # Build the payload for the STK push request
    payload = {
        "BusinessShortCode": settings.SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,  # Replace with the desired amount
        "PartyA": 25475880045,  # Replace with the customer's phone number in international format
        "PartyB": settings.SHORT_CODE,
        "PhoneNumber": 254758800045,  # Same as PartyA or another authorized number
        "CallBackURL": settings.CALLBACK_URL,
        "AccountReference": "YOUR_REFERENCE",  # Could be an order number, customer ID, etc.
        "TransactionDesc": "Payment for services"
    }

    # Send the POST request to MPESA STK push endpoint
    response = requests.post(settings.STK_PUSH_URL, json=payload, headers=headers)
    
    # For debugging: you can print or log response.text
    print(response.text)
    
    # Return the response back as JSON
    return JsonResponse(response.json())

@csrf_exempt
def mpesa_callback(request):
    """
    Handles the callback from MPESA after a transaction is processed.
    MPESA sends the transaction result to this URL.
    """
    if request.method == "POST":
        import json
        callback_data = json.loads(request.body)
        # Here you can process the callback_data, update your database, log transaction status, etc.
        print("Callback received:", callback_data)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

def payment_success(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)
    return render(request, 'payments/payment_success.html', {'parcel': parcel})

def payment_cancel(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)
    return render(request, "payments/payment_cancel.html", {"parcel": parcel})