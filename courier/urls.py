# courier/urls.py
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', LogoutView.as_view(next_page="/login/"), name="logout"),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('add_parcel/', views.add_parcel, name='add_parcel'),
    path('parcel_confirmation/<int:parcel_id>/', views.parcel_confirmation, name='parcel_confirmation'),
    path('delete_parcel/<int:parcel_id>/', views.delete_parcel, name='delete_parcel'),
]
