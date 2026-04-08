"""clinic_system URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_views import admin_dashboard
from django.shortcuts import redirect
from accounts.views import dashboard
from .views import serve_firestore_pdf
from reports.admin_stats import (
    stats_dashboard, stats_patients, stats_appointments,
    stats_billing, stats_pharmacy, stats_laboratory, stats_staff,
    export_stats_csv, export_stats_excel,
)

# Admin branding
admin.site.site_header = 'PhysioNutrition Clinic Administration'
admin.site.site_title = 'PhysioNutrition Admin'
admin.site.index_title = 'Dashboard'
admin.site.site_url = '/dashboard/'
admin.site.enable_nav_sidebar = False

# Inject dashboard stats into admin index
_original_index = admin.site.__class__.index

def _patched_index(self, request, extra_context=None):
    from patients.models import Patient
    from appointments.models import Appointment
    from billing.models import Invoice
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    User = get_user_model()
    today = timezone.now().date()
    extra_context = extra_context or {}
    extra_context.update({
        'total_patients': Patient.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'todays_appointments': Appointment.objects.filter(appointment_date=today).count(),
        'total_invoices': Invoice.objects.count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
    })
    return _original_index(self, request, extra_context)

admin.site.__class__.index = _patched_index

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django Jet URLS
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django Jet dashboard URLS
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    # Stats URLs — must come BEFORE admin.site.urls catch-all
    path('admin/stats/', stats_dashboard, name='stats_dashboard'),
    path('admin/stats/patients/', stats_patients, name='stats_patients'),
    path('admin/stats/appointments/', stats_appointments, name='stats_appointments'),
    path('admin/stats/billing/', stats_billing, name='stats_billing'),
    path('admin/stats/pharmacy/', stats_pharmacy, name='stats_pharmacy'),
    path('admin/stats/laboratory/', stats_laboratory, name='stats_laboratory'),
    path('admin/stats/staff/', stats_staff, name='stats_staff'),
    path('admin/stats/export/<str:module>/csv/', export_stats_csv, name='export_stats_csv'),
    path('admin/stats/export/<str:module>/excel/', export_stats_excel, name='export_stats_excel'),
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
