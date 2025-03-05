# courier/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, ParcelForm
from django.contrib.auth.decorators import login_required
from .models import Parcel, CustomerProfile, CustomUser

def home(request):
    """
    A simple view that renders the home page with system details.
    """
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated profile based on role
            if user.role == 'customer':
                # Create a CustomerProfile (you could extend this with more data)
                from .models import CustomerProfile
                CustomerProfile.objects.create(user=user, address='', phone='')
            elif user.role == 'staff':
                from .models import StaffProfile
                StaffProfile.objects.create(user=user, phone='', branch=None)
            # Log the user in after signup
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    # Display different info based on role; here we show parcels for a customer
    if request.user.role == 'customer':
        customer_profile = CustomerProfile.objects.get(user=request.user)
        parcels = Parcel.objects.filter(sender=customer_profile)
    else:
        parcels = Parcel.objects.all()
    return render(request, 'courier/dashboard.html', {'parcels': parcels})

@login_required
def add_parcel(request):
    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            # Assume the logged-in user is the sender if they are a customer
            if request.user.role == 'customer':
                customer_profile = CustomerProfile.objects.get(user=request.user)
                parcel.sender = customer_profile
            parcel.status = 'Pending'
            parcel.save()
            return redirect('dashboard')
    else:
        form = ParcelForm()
    return render(request, 'courier/addparcel.html', {'form': form})
