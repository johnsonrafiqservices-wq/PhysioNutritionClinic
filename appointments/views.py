from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, datetime, timedelta
import calendar
from .models import Appointment, Service, TreatmentSession, NutritionConsultation
from .forms import AppointmentForm, TreatmentSessionForm, NutritionConsultationForm
from patients.models import Patient
from clinic_system.pagination_utils import paginate_queryset

@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related('patient', 'service', 'provider', 'created_by').all()
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    provider_query = request.GET.get('provider')
    
    # Filter by date range
    if date_from:
        appointments = appointments.filter(appointment_date__gte=date_from)
    if date_to:
        appointments = appointments.filter(appointment_date__lte=date_to)
    
    # If no date filters, show all appointments (not just today's)
    # Remove the default filter to today's appointments
    
    # Filter by status
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Search functionality
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__patient_id__icontains=search_query) |
            Q(service__name__icontains=search_query) |
            Q(provider__first_name__icontains=search_query) |
            Q(provider__last_name__icontains=search_query)
        )
    
    # Filter by provider name
    if provider_query:
        appointments = appointments.filter(
            Q(provider__first_name__icontains=provider_query) |
            Q(provider__last_name__icontains=provider_query)
        )
    
    # Filter by provider (for doctors/therapists)
    if hasattr(request.user, 'role') and request.user.role in ['doctor', 'nutritionist']:
        appointments = appointments.filter(provider=request.user)
    
    # Order by appointment date and time
    appointments = appointments.order_by('appointment_date', 'appointment_time')
    
    # Paginate with dynamic page size
    pagination_data = paginate_queryset(request, appointments, default_page_size=25)
    
    # Calculate statistics for bottom cards (today's appointments)
    from datetime import date
    today = date.today()
    
    # Base queryset for today's stats (respecting provider filter for doctors/nutritionists)
    today_appointments = Appointment.objects.filter(appointment_date=today)
    if hasattr(request.user, 'role') and request.user.role in ['doctor', 'nutritionist']:
        today_appointments = today_appointments.filter(provider=request.user)
    
    today_appointments_count = today_appointments.count()
    completed_today_count = today_appointments.filter(status='completed').count()
    pending_appointments_count = today_appointments.filter(status__in=['scheduled', 'confirmed']).count()
    cancelled_today_count = today_appointments.filter(status='cancelled').count()
    
    # Get data for appointment creation modal
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    all_patients = Patient.objects.filter(is_active=True).order_by('first_name', 'last_name')
    services = Service.objects.filter(is_active=True).order_by('category', 'name')
    providers = User.objects.filter(role__in=['doctor', 'nutritionist', 'physiotherapist'], is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'page_obj': pagination_data['page_obj'],
        'appointments': pagination_data['items'],
        'date_from': date_from,
        'date_to': date_to,
        'status': status_filter,
        'search_query': search_query,
        'provider_query': provider_query,
        'status_choices': Appointment.STATUS_CHOICES,
        'page_size': pagination_data['page_size'],
        'query_string': pagination_data['query_string'],
        'today_appointments_count': today_appointments_count,
        'completed_today_count': completed_today_count,
        'pending_appointments_count': pending_appointments_count,
        'cancelled_today_count': cancelled_today_count,
        'all_patients': all_patients,
        'services': services,
        'providers': providers,
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.created_by = request.user
            appointment.duration_minutes = appointment.service.duration_minutes
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/appointment_create.html', {'form': form})

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to update this appointment.")
        return redirect('appointments:appointment_detail', pk=appointment.pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            if updated_appointment.service and not updated_appointment.duration_minutes:
                updated_appointment.duration_minutes = updated_appointment.service.duration_minutes
            updated_appointment.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments:appointment_detail', pk=updated_appointment.pk)
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'title': 'Update Appointment',
    }
    return render(request, 'appointments/appointment_form.html', context)

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'service', 'provider', 'created_by'),
        pk=pk
    )
    
    # Check if treatment session or nutrition consultation exists
    treatment_session = getattr(appointment, 'treatment_session', None)
    nutrition_consultation = getattr(appointment, 'nutrition_consultation', None)
    
    context = {
        'appointment': appointment,
        'treatment_session': treatment_session,
        'nutrition_consultation': nutrition_consultation,
    }
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def appointment_update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {appointment.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('appointments:appointment_detail', pk=pk)

@login_required
def treatment_session_create(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    
    # Check if treatment session already exists
    if hasattr(appointment, 'treatment_session'):
        messages.info(request, 'Treatment session already exists for this appointment.')
        return redirect('appointments:treatment_session_update', appointment_pk=appointment_pk)
    
    if request.method == 'POST':
        form = TreatmentSessionForm(request.POST)
        if form.is_valid():
            treatment_session = form.save(commit=False)
            treatment_session.appointment = appointment
            if form.cleaned_data.get('session_completed'):
                treatment_session.completed_at = datetime.now()
            treatment_session.save()
            
            # Update appointment status
            appointment.status = 'completed' if treatment_session.session_completed else 'in_progress'
            appointment.save()
            
            messages.success(request, 'Treatment session recorded successfully!')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = TreatmentSessionForm()
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/treatment_session.html', context)

@login_required
def treatment_session_update(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    treatment_session = get_object_or_404(TreatmentSession, appointment=appointment)
    
    if request.method == 'POST':
        form = TreatmentSessionForm(request.POST, instance=treatment_session)
        if form.is_valid():
            treatment_session = form.save(commit=False)
            if form.cleaned_data.get('session_completed') and not treatment_session.completed_at:
                treatment_session.completed_at = datetime.now()
            treatment_session.save()
            
            # Update appointment status
            appointment.status = 'completed' if treatment_session.session_completed else 'in_progress'
            appointment.save()
            
            messages.success(request, 'Treatment session updated successfully!')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = TreatmentSessionForm(instance=treatment_session)
    
    context = {
        'form': form,
        'appointment': appointment,
        'treatment_session': treatment_session,
    }
    return render(request, 'appointments/treatment_session.html', context)

@login_required
def nutrition_consultation_create(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    
    # Check if nutrition consultation already exists
    if hasattr(appointment, 'nutrition_consultation'):
        messages.info(request, 'Nutrition consultation already exists for this appointment.')
        return redirect('appointments:nutrition_consultation_update', appointment_pk=appointment_pk)
    
    if request.method == 'POST':
        form = NutritionConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.appointment = appointment
            if form.cleaned_data.get('consultation_completed'):
                consultation.completed_at = datetime.now()
            consultation.save()
            
            # Update appointment status
            appointment.status = 'completed' if consultation.consultation_completed else 'in_progress'
            appointment.save()
            
            messages.success(request, 'Nutrition consultation recorded successfully!')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = NutritionConsultationForm()
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/nutrition_consultation.html', context)

@login_required
def confirm_appointment(request, pk):
    """
    View to confirm an appointment.
    Accessible by staff and the patient the appointment belongs to.
    Handles both GET and POST requests.
    """
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permissions - either staff or the patient
    if not (request.user.is_staff or request.user == appointment.patient.user):
        messages.error(request, "You don't have permission to confirm this appointment.")
        return redirect('login')
    
    if request.method == 'POST':
        # Update appointment status
        appointment.status = 'confirmed'
        appointment.save()
        
        # Add success message
        messages.success(request, f"Appointment for {appointment.patient} has been confirmed.")
        
        # Redirect back to appointment detail or dashboard
        if request.user.is_staff:
            return redirect('appointments:appointment_detail', pk=appointment.pk)
        return redirect('patients:patient_dashboard')
    
    # For GET requests, show a confirmation page
    context = {
        'appointment': appointment,
        'title': 'Confirm Appointment',
    }
    return render(request, 'appointments/appointment_confirm.html', context)

@login_required
def nutrition_consultation_update(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    consultation = get_object_or_404(NutritionConsultation, appointment=appointment)
    
    if request.method == 'POST':
        form = NutritionConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            consultation = form.save(commit=False)
            if form.cleaned_data.get('consultation_completed') and not consultation.completed_at:
                consultation.completed_at = datetime.now()
            consultation.save()
            
            # Update appointment status
            appointment.status = 'completed' if consultation.consultation_completed else 'in_progress'
            appointment.save()
            
            messages.success(request, 'Nutrition consultation updated successfully!')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = NutritionConsultationForm(instance=consultation)
    
    context = {
        'form': form,
        'appointment': appointment,
        'consultation': consultation,
    }
    return render(request, 'appointments/nutrition_consultation.html', context)

@login_required
def calendar_view(request):
    # Get current date or requested date
    today = date.today()
    
    # If no specific month/year requested, try to show a month with appointments
    if not request.GET.get('year') and not request.GET.get('month'):
        # Check if there are appointments in current month
        current_month_appointments = Appointment.objects.filter(
            appointment_date__year=today.year,
            appointment_date__month=today.month
        ).exists()
        
        if not current_month_appointments:
            # Find the most recent month with appointments
            recent_appointment = Appointment.objects.order_by('-appointment_date').first()
            if recent_appointment:
                year = recent_appointment.appointment_date.year
                month = recent_appointment.appointment_date.month
            else:
                year = today.year
                month = today.month
        else:
            year = today.year
            month = today.month
    else:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    
    # Ensure valid month/year
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # Get calendar data
    cal = calendar.Calendar(firstweekday=0)  # Monday = 0
    month_days = list(cal.itermonthdates(year, month))
    
    # Get appointments for the month
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)
    
    appointments = Appointment.objects.select_related('patient', 'service', 'provider', 'created_by').filter(
        appointment_date__range=[month_start, month_end]
    ).order_by('appointment_date', 'appointment_time')
    
    # Filter by provider if user is doctor/nutritionist
    if hasattr(request.user, 'role') and request.user.role in ['doctor', 'nutritionist']:
        appointments = appointments.filter(provider=request.user)
    
    # Group appointments by date
    appointments_by_date = {}
    for appointment in appointments:
        date_key = appointment.appointment_date
        if date_key not in appointments_by_date:
            appointments_by_date[date_key] = []
        appointments_by_date[date_key].append(appointment)
    
    # Create calendar weeks
    weeks = []
    week = []
    for day in month_days:
        if len(week) == 7:
            weeks.append(week)
            week = []
        
        day_appointments = appointments_by_date.get(day, [])
        week.append({
            'date': day,
            'is_current_month': day.month == month,
            'is_today': day == today,
            'appointments': day_appointments,
            'appointment_count': len(day_appointments)
        })
    
    if week:
        weeks.append(week)
    
    # Navigation dates
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # Check if this is an AJAX request for JSON data
    if request.headers.get('Accept') == 'application/json' or 'application/json' in request.headers.get('Accept', ''):
        # Return JSON data for AJAX requests
        appointments_data = {}
        for date_key, day_appointments in appointments_by_date.items():
            appointments_data[date_key.strftime('%Y-%m-%d')] = [
                {
                    'id': apt.id,
                    'appointment_time': apt.appointment_time.strftime('%H:%M'),
                    'patient_name': apt.patient.get_full_name(),
                    'service_name': apt.service.name if apt.service else 'No Service',
                    'provider_name': apt.provider.get_full_name(),
                    'status': apt.status
                }
                for apt in day_appointments
            ]
        
        return JsonResponse({
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'appointments_by_date': appointments_data,
            'total_appointments': appointments.count(),
        })
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'weeks': weeks,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'appointments_by_date': appointments_by_date,
        'total_appointments': appointments.count(),
    }
    
    return render(request, 'appointments/calendar_view.html', context)

@login_required
def calendar_day_detail(request, year, month, day):
    """Get appointments for a specific day (AJAX endpoint)"""
    try:
        selected_date = date(year, month, day)
    except ValueError:
        return JsonResponse({'error': 'Invalid date'}, status=400)
    
    appointments = Appointment.objects.select_related('patient', 'service', 'provider', 'created_by').filter(
        appointment_date=selected_date
    ).order_by('appointment_time')
    
    # Filter by provider if user is doctor/nutritionist
    if hasattr(request.user, 'role') and request.user.role in ['doctor', 'nutritionist']:
        appointments = appointments.filter(provider=request.user)
    
    appointments_data = []
    for appointment in appointments:
        appointments_data.append({
            'id': appointment.id,
            'patient_name': appointment.patient.get_full_name(),
            'patient_id': appointment.patient.patient_id,
            'service': appointment.service.name,
            'provider': f"{appointment.provider.first_name} {appointment.provider.last_name}",
            'time': appointment.appointment_time.strftime('%H:%M'),
            'duration': appointment.duration_minutes,
            'status': appointment.status,
            'status_display': appointment.get_status_display(),
            'notes': appointment.notes,
        })
    
    return JsonResponse({
        'date': selected_date.strftime('%Y-%m-%d'),
        'date_display': selected_date.strftime('%B %d, %Y'),
        'appointments': appointments_data
    })

@login_required
def appointment_cancel(request, pk):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        # Update appointment status to cancelled
        appointment.status = 'cancelled'
        appointment.save()
        
        messages.success(request, f'Appointment for {appointment.patient.get_full_name()} has been cancelled.')
        
        # Redirect to the referring page or appointment list
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('appointments:appointment_list')
    
    # For GET requests, show confirmation page
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_cancel_confirm.html', context)

@login_required
def appointment_reschedule(request, pk):
    """Reschedule an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        # Get new date and time from form
        new_date = request.POST.get('appointment_date')
        new_time = request.POST.get('appointment_time')
        
        if new_date and new_time:
            appointment.appointment_date = new_date
            appointment.appointment_time = new_time
            appointment.save()
            
            messages.success(request, f'Appointment rescheduled to {appointment.appointment_date} at {appointment.appointment_time}.')
            
            # Redirect to the referring page or appointment list
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('appointments:appointment_detail', pk=appointment.pk)
        else:
            messages.error(request, 'Please provide both date and time.')
    
    # For GET requests, show reschedule form
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_reschedule.html', context)


# ==================== AJAX-ONLY VIEWS ====================

@login_required
def appointment_create_ajax(request):
    """AJAX-only appointment creation view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = AppointmentForm(request.POST)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.created_by = request.user
        appointment.duration_minutes = appointment.service.duration_minutes
        appointment.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': f'Appointment for {appointment.patient.get_full_name()} scheduled successfully!',
            'appointment_id': appointment.id,
            'redirect_url': reverse('appointments:appointment_detail', kwargs={'pk': appointment.pk})
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@login_required
def appointment_update_ajax(request, pk):
    """AJAX-only appointment update view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': "You don't have permission to update this appointment."
        }, status=403)
    
    form = AppointmentForm(request.POST, instance=appointment)
    if form.is_valid():
        updated_appointment = form.save(commit=False)
        if updated_appointment.service and not updated_appointment.duration_minutes:
            updated_appointment.duration_minutes = updated_appointment.service.duration_minutes
        updated_appointment.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': 'Appointment updated successfully!',
            'appointment_id': updated_appointment.id,
            'redirect_url': reverse('appointments:appointment_detail', kwargs={'pk': updated_appointment.pk})
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@login_required
def appointment_cancel_ajax(request, pk):
    """AJAX-only appointment cancellation view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Update appointment status to cancelled
    appointment.status = 'cancelled'
    appointment.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Appointment for {appointment.patient.get_full_name()} has been cancelled.',
        'appointment_id': appointment.id
    })


@login_required
def appointment_reschedule_ajax(request, pk):
    """AJAX-only appointment reschedule view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Get new date and time from form
    new_date = request.POST.get('appointment_date')
    new_time = request.POST.get('appointment_time')
    
    if not new_date or not new_time:
        return JsonResponse({
            'success': False,
            'message': 'Please provide both date and time.'
        }, status=400)
    
    appointment.appointment_date = new_date
    appointment.appointment_time = new_time
    appointment.save()
    
    from django.urls import reverse
    return JsonResponse({
        'success': True,
        'message': f'Appointment rescheduled to {appointment.appointment_date} at {appointment.appointment_time}.',
        'appointment_id': appointment.id,
        'redirect_url': reverse('appointments:appointment_detail', kwargs={'pk': appointment.pk})
    })


@login_required
def treatment_session_ajax(request, appointment_pk):
    """AJAX-only treatment session create/update view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    
    # Check if treatment session already exists
    treatment_session = getattr(appointment, 'treatment_session', None)
    
    if treatment_session:
        # Update existing session
        form = TreatmentSessionForm(request.POST, instance=treatment_session)
    else:
        # Create new session
        form = TreatmentSessionForm(request.POST)
    
    if form.is_valid():
        treatment_session = form.save(commit=False)
        treatment_session.appointment = appointment
        
        if form.cleaned_data.get('session_completed'):
            if not treatment_session.completed_at:
                treatment_session.completed_at = datetime.now()
        
        treatment_session.save()
        
        # Update appointment status
        appointment.status = 'completed' if treatment_session.session_completed else 'in_progress'
        appointment.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': 'Treatment session recorded successfully!',
            'appointment_id': appointment.id,
            'redirect_url': reverse('appointments:appointment_detail', kwargs={'pk': appointment.pk})
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@login_required
def nutrition_consultation_ajax(request, appointment_pk):
    """AJAX-only nutrition consultation create/update view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    
    # Check if nutrition consultation already exists
    consultation = getattr(appointment, 'nutrition_consultation', None)
    
    if consultation:
        # Update existing consultation
        form = NutritionConsultationForm(request.POST, instance=consultation)
    else:
        # Create new consultation
        form = NutritionConsultationForm(request.POST)
    
    if form.is_valid():
        consultation = form.save(commit=False)
        consultation.appointment = appointment
        
        if form.cleaned_data.get('consultation_completed'):
            if not consultation.completed_at:
                consultation.completed_at = datetime.now()
        
        consultation.save()
        
        # Update appointment status
        appointment.status = 'completed' if consultation.consultation_completed else 'in_progress'
        appointment.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': 'Nutrition consultation recorded successfully!',
            'appointment_id': appointment.id,
            'redirect_url': reverse('appointments:appointment_detail', kwargs={'pk': appointment.pk})
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)
 