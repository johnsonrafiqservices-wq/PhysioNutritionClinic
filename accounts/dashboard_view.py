"""
Complete Dashboard View for Excellence Med Care
This replaces the simple dashboard view in accounts/views.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta


@login_required
def dashboard(request):
    """
    Main dashboard view compatible with your system's apps:
    - patients (not ehr)
    - inventory (not pharmacy)
    - laboratory (not lab)
    - appointments, billing, medical_records, reports
    """
    context = {}
    today = timezone.now().date()
    current_time = timezone.now()
    
    # Add current date and time for display
    context['current_date'] = today.strftime('%A, %B %d, %Y')
    context['current_time'] = current_time.strftime('%I:%M %p')
    
    # Import models (use try/except to handle missing models gracefully)
    try:
        from patients.models import Patient
        context['patient_count'] = Patient.objects.count()
    except:
        context['patient_count'] = 0
    
    try:
        from appointments.models import Appointment
        today_appointments = Appointment.objects.filter(
            appointment_date__date=today
        ).select_related('patient').order_by('appointment_date')
        
        context['appointment_count'] = today_appointments.count()
        context['today_appointments'] = today_appointments[:10]
        context['completed_appointments'] = today_appointments.filter(
            status='completed'
        ).count()
    except:
        context['appointment_count'] = 0
        context['today_appointments'] = []
        context['completed_appointments'] = 0
    
    try:
        from billing.models import Invoice
        pending_invoices = Invoice.objects.filter(status='pending')
        context['pending_invoices'] = pending_invoices.count()
        context['pending_amount'] = sum(
            invoice.total_amount for invoice in pending_invoices
        )
    except:
        context['pending_invoices'] = 0
        context['pending_amount'] = 0
    
    try:
        from billing.models import Payment
        context['recent_payments'] = Payment.objects.all().order_by(
            '-created_at'
        )[:10]
    except:
        context['recent_payments'] = []
    
    try:
        from laboratory.models import LabTest
        context['pending_lab_tests'] = LabTest.objects.filter(
            status__in=['requested', 'pending']
        ).count()
        context['todays_lab_tests'] = LabTest.objects.filter(
            created_at__date=today
        ).count()
    except:
        context['pending_lab_tests'] = 0
        context['todays_lab_tests'] = 0
    
    try:
        from inventory.models import Drug
        # Check for low stock items (assuming you have a quantity field)
        context['low_stock_count'] = Drug.objects.filter(
            quantity__lte=10  # Adjust based on your model
        ).count() if hasattr(Drug, 'quantity') else 0
    except:
        context['low_stock_count'] = 0
    
    # Add user info
    context['user'] = request.user
    context['role'] = request.user.role if hasattr(request.user, 'role') else 'staff'
    
    return render(request, 'dashboard_fixed.html', context)
