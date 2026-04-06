"""clinic_system URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_views import admin_dashboard
from django.shortcuts import redirect
from accounts.views import dashboard
from .views import serve_firestore_pdf

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django Jet URLS
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django Jet dashboard URLS
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:login' if not request.user.is_authenticated else 'dashboard'), name='root_redirect'),
    path('dashboard/', dashboard, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('billing/', include('billing.urls')),
    path('medical-records/', include('medical_records.urls')),
    path('reports/', include('reports.urls')),
    path('settings/', include('clinic_settings.urls')),
    path('laboratory/', include('laboratory.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('staff/', include('staff_management.urls')),
    path('budget/', include('budget.urls')),
    path('firestore-pdf/<str:subfolder>/<str:filename>', serve_firestore_pdf, name='serve_firestore_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
