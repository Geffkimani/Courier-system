from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from courier import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_parcel/', views.add_parcel, name='add_parcel'),

    # Redirect root URL to the dashboard or signup, for example
    path('', lambda request: redirect('dashboard')),  # Or 'signup', depending on your flow
]
