from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.contrib.auth import get_user_model
from patients.models import Patient
from appointments.models import Appointment
from billing.models import Invoice

User = get_user_model()

class AlafiaAdminSite(AdminSite):
    site_header = 'Alafia Point Wellness Clinic Administration'
    site_title = 'Alafia Admin'
    index_title = 'Welcome to Alafia Point Wellness Clinic Administration'

    def index(self, request, extra_context=None):
        """
        Display the main admin index page with Alafia styling and statistics.
        """
        # Get statistics
        total_patients = Patient.objects.count()
        total_appointments = Appointment.objects.count()
        total_invoices = Invoice.objects.count()
        total_staff = User.objects.filter(is_staff=True).count()
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'total_invoices': total_invoices,
            'total_staff': total_staff,
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = AlafiaAdminSite(name='alafia_admin')
