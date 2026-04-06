from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from patients.models import Patient
from appointments.models import Appointment
from billing.models import Invoice

User = get_user_model()

@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics"""
    
    # Get statistics
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_invoices = Invoice.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    
    context = {
        'title': 'Dashboard',
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_invoices': total_invoices,
        'total_staff': total_staff,
    }
    
    return render(request, 'admin/index.html', context)
