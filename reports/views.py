import csv
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from courier.models import Parcel, CustomerProfile
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from django.db.models import Count,Sum, Avg


def reports_dashboard(request):
    return render(request, "reports/reports_dashboard.html")

def parcel_report(request):
    parcels = Parcel.objects.all()
    return render(request, "reports/parcel_report.html", {"parcels": parcels})

def payment_report(request):
    payments = Payment.objects.all()
    return render(request, "reports/payment_report.html", {"payments": payments})

def customer_report(request):
    customers = CustomerProfile.objects.all()
    return render(request, "reports/customer_report.html", {"customers": customers})

def customer_report_view(request):
    """Render the HTML page with the parcel report"""
    customer = CustomerProfile.objects.get(user=request.user)
    parcels = Parcel.objects.filter(receiver=customer)
    return render(request, 'customer_report.html', {'parcels': parcels})

def customer_report_download(request):
    """Generate and download the report as a CSV file"""
    customer = CustomerProfile.objects.get(user=request.user)
    parcels = Parcel.objects.filter(receiver=customer)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tracking Number', 'Destination', 'Status', 'Delivery Date'])

    for parcel in parcels:
        writer.writerow([parcel.tracking_number, parcel.branch_to.name, parcel.status, parcel.delivery_date])

    return response

@login_required
def customer_parcel_history(request):
    # Assuming sender is linked to CustomerProfile and CustomerProfile is related to request.user
    parcels = Parcel.objects.filter(sender=request.user.customerprofile).order_by('-sent_date')
    total_parcels = parcels.count()
    total_weight = parcels.aggregate(total=Sum('weight'))['total'] or 0

    context = {
        'parcels': parcels,
        'total_parcels': total_parcels,
        'total_weight': total_weight,
    }
    return render(request, 'reports/customer_parcel_history.html', context)

@login_required
def customer_status_report(request):
    parcels = Parcel.objects.filter(sender=request.user.customerprofile)
    in_transit = parcels.filter(status="In Transit").count()
    delivered = parcels.filter(status="Delivered").count()
    pending = parcels.filter(status="Pending").count()
    
    context = {
        'in_transit': in_transit,
        'delivered': delivered,
        'pending': pending,
    }
    return render(request, 'reports/customer_status_report.html', context)


@login_required
def customer_activity_report(request):
    parcels = Parcel.objects.filter(sender=request.user.customerprofile)
    monthly_report = parcels.annotate(month=TruncMonth('sent_date')) \
                            .values('month') \
                            .annotate(count=Count('id')) \
                            .order_by('month')
    context = {
        'monthly_report': monthly_report,
    }
    return render(request, 'reports/customer_activity_report.html', context)


@login_required
def pending_deliveries_report(request):
    pending_parcels = Parcel.objects.filter(status="Pending")
    context = {
        'pending_parcels': pending_parcels,
    }
    return render(request, 'reports/pending_deliveries_report.html', context)

@login_required
def parcels_by_branch_report(request):
    parcels_by_branch = Parcel.objects.values('branch_from__name') \
                                      .annotate(count=Count('id')) \
                                      .order_by('branch_from__name')
    context = {
        'parcels_by_branch': parcels_by_branch,
    }
    return render(request, 'reports/parcels_by_branch_report.html', context)

@login_required
def delayed_deliveries_report(request):
    delayed_parcels = Parcel.objects.filter(status="In Transit", expected_delivery_date__lt=now())
    context = {
        'delayed_parcels': delayed_parcels,
    }
    return render(request, 'reports/delayed_deliveries_report.html', context)


@login_required
def total_revenue_report(request):
    total_revenue = Parcel.objects.aggregate(total=Sum('delivery_fee'))['total'] or 0
    context = {'total_revenue': total_revenue}
    return render(request, 'reports/total_revenue_report.html', context)


@login_required
def top_customers_report(request):
    # Group parcels by sender (customer profile) and count parcels
    top_customers = Parcel.objects.values('sender__user__username') \
                                  .annotate(count=Count('id')) \
                                  .order_by('-count')[:5]
    context = {'top_customers': top_customers}
    return render(request, 'reports/top_customers_report.html', context)

@login_required
def operational_efficiency_report(request):
    avg_delivery_time = Parcel.objects.filter(status="Delivered").aggregate(avg_time=Avg('delivery_time'))['avg_time']
    context = {'avg_delivery_time': avg_delivery_time}
    return render(request, 'reports/operational_efficiency_report.html', context)

@login_required
def export_parcels_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="parcels_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Tracking Number", "Sender", "Destination", "Weight", "Status", "Sent Date"])

    parcels = Parcel.objects.all()  # Adjust the queryset as needed
    for parcel in parcels:
        writer.writerow([
            parcel.tracking_number,
            parcel.sender.user.username,  # Assuming sender is CustomerProfile
            parcel.branch_to.name,
            parcel.weight,
            parcel.status,
            parcel.sent_date.strftime("%Y-%m-%d %H:%M:%S") if parcel.sent_date else "N/A"
        ])

    return response

@login_required
def export_parcels_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="parcels_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    y = 750
    p.drawString(50, y, "Parcel Report")
    y -= 30

    parcels = Parcel.objects.all()  # Adjust query as needed
    for parcel in parcels:
        line = f"{parcel.tracking_number} - {parcel.sender.user.username} - {parcel.branch_to.name} - {parcel.status}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    p.showPage()
    p.save()
    return response
