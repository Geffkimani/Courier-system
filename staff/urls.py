from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("login/", views.staff_login, name="staff_login"),
    path("dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("update_parcel_status/<int:parcel_id>/", views.update_parcel_status, name="update_parcel_status"),
    path("operational_report/", views.operational_report, name="operational_report"),
    path("logout/", LogoutView.as_view(next_page="/staff/login/"), name="staff_logout"),
    path("register/", views.register_staff, name="register_staff"),
    path("add_parcel/", views.add_parcel_by_staff, name="staff_add_parcel"),
    path('dashboard/report/', views.generate_report, name='generate_report'),
]
