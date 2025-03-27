import os

from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from courier.models import Parcel, StaffProfile, Branch
from .forms import StaffRegistrationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from staff.models import StaffProfile
from courier.utils import generate_unique_tracking_number
import random
import string

def generate_unique_tracking_number():
    # If not already imported from courier.models
    while True:
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Parcel.objects.filter(tracking_number=tracking_number).exists():
            return tracking_number

def is_staff_user(user):
    return user.is_staff

def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def register_staff(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff account created successfully.")
            return redirect('staff_dashboard')
    else:
        form = StaffRegistrationForm()
    return render(request, 'staff/register_staff.html', {'form': form})


def staff_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect("staff_dashboard")
            else:
                messages.error(request, "You are not authorized to access the staff dashboard.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "staff/staff_login.html")

@login_required
@user_passes_test(is_staff_user)
def staff_dashboard(request):
    pending_parcels = Parcel.objects.filter(status="Pending")
    in_transit_parcels = Parcel.objects.filter(status="In Transit")
    delivered_parcels = Parcel.objects.filter(status="Delivered")

    # Fetch available reports
    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")  # We are Assuming reports are stored in MEDIA/reports
    available_reports = []

    if os.path.exists(reports_dir):
        available_reports = [
            f for f in os.listdir(reports_dir) if f.endswith(".pdf") or f.endswith(".csv")
        ]
    context = {
        'pending_parcels': pending_parcels,
        'in_transit_parcels': in_transit_parcels,
        'delivered_parcels': delivered_parcels,
        "available_reports": available_reports,
    }
    return render(request, "staff/dashboard.html", context)

@login_required
@user_passes_test(is_staff_user)
def update_parcel_status(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Pending", "In Transit", "Delivered"]:
            parcel.status = new_status
            # Optionally, if delivered, record delivery date
            if new_status == "Delivered":
                parcel.delivery_date = timezone.now()
            parcel.save()
            messages.success(request, "Parcel status updated.")
        else:
            messages.error(request, "Invalid status selected.")
        return redirect("staff_dashboard")
    return render(request, "staff/update_parcel_status.html", {"parcel": parcel})


@login_required
@user_passes_test(is_staff_user)
def operational_report(request):
    total_parcels = Parcel.objects.count()
    pending = Parcel.objects.filter(status="Pending").count()
    in_transit = Parcel.objects.filter(status="In Transit").count()
    delivered = Parcel.objects.filter(status="Delivered").count()
    context = {
        'total_parcels': total_parcels,
        'pending': pending,
        'in_transit': in_transit,
        'delivered': delivered,
    }
    return render(request, "staff/operational_report.html", context)

@login_required
@user_passes_test(is_staff_user)
def add_parcel_by_staff(request):
    branches = Branch.objects.all()

    if request.method == 'POST':
        sender_name = request.POST.get('sender')
        branch_from_id = request.POST.get('branch_from')
        branch_to_id = request.POST.get('branch_to')
        description = request.POST.get('description')
        weight = request.POST.get('weight')

        # Basic validation
        if not sender_name or not branch_from_id or not branch_to_id or not description or not weight:
            messages.error(request, "All fields are required.")
            return redirect('staff_add_parcel')

        try:
            weight = float(weight)
        except ValueError:
            messages.error(request, "Weight must be a valid number.")
            return redirect('staff_add_parcel')

        branch_from = get_object_or_404(Branch, id=branch_from_id)
        branch_to = get_object_or_404(Branch, id=branch_to_id)

        #Get the staff profile from the logged-in user
        staff_profile = get_object_or_404(StaffProfile, user=request.user)

        # Create the parcel
        parcel = Parcel.objects.create(
            sender_name=sender_name,
            branch_from=branch_from,
            branch_to=branch_to,
            description=description,
            weight=weight,
            tracking_number=generate_unique_tracking_number(),
            status='Pending',
            created_by_staff=staff_profile
        )

        messages.success(request, f"Parcel {parcel.tracking_number} added successfully.")
        return redirect('staff_dashboard')

    context = {'branches': branches}
    return render(request, 'staff/add_parcel.html', context)

@login_required
@user_passes_test(is_staff_user)
def operational_report(request):
    total_parcels = Parcel.objects.count()
    pending = Parcel.objects.filter(status="Pending").count()
    in_transit = Parcel.objects.filter(status="In Transit").count()
    delivered = Parcel.objects.filter(status="Delivered").count()
    context = {
        'total_parcels': total_parcels,
        'pending': pending,
        'in_transit': in_transit,
        'delivered': delivered,
    }
    return render(request, "staff/operational_report.html", context)

def generate_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="parcels_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tracking Number', 'Sender Name', 'Destination', 'Status', 'Delivery Date'])

    parcels = Parcel.objects.all()
    for parcel in parcels:
        writer.writerow([parcel.tracking_number, parcel.sender_name, parcel.branch_to.name, parcel.status, parcel.delivery_date])

    return response