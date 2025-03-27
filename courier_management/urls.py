from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courier.urls')),
    path('staff/', include('staff.urls')),
    path('reports/', include('reports.urls')),
    path('payments/', include('payments.urls', namespace='payments')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)