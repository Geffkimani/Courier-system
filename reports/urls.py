from django.urls import path
from . import views

urlpatterns = [
    #path("", views.reports_dashboard, name="reports_dashboard"),
    path("parcel-report/", views.parcel_report, name="parcel_report"),
    path("payment-report/", views.payment_report, name="payment_report"),
    path("customer-report/", views.customer_report, name="customer_report"),
    path('customer-report/download/', views.customer_report_download, name='customer_report_download'),
]
