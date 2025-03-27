from django.urls import path, include
from .views import (
    lipa_na_mpesa_online,
    mpesa_callback,
    process_payment,
    payment_success,
    payment_cancel,
    proceed_to_payment,
)

app_name = "payments"

urlpatterns = [
    path('mpesa/stk-push/', lipa_na_mpesa_online, name='stk_push'),
    path('mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('process/<int:parcel_id>/', process_payment, name='process_payment'),
    path('success/<int:parcel_id>/', payment_success, name='payment_success'),
    path('cancel/<int:parcel_id>/', payment_cancel, name='payment_cancel'),
    path('pay/<int:parcel_id>/', proceed_to_payment, name='proceed_to_payment'),
]
