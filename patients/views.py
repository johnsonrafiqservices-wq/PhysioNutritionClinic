import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from datetime import datetime, time, timedelta
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from .models import Patient, PatientGroup, VitalSigns, Triage, Assessment, TriageAssessment
from .forms import PatientForm, VisitingPatientForm, VitalSignsForm, TriageForm, AssessmentForm, TriageAssessmentForm
from appointments.models import Appointment, Service
from accounts.permissions import (
    app_access_required, permission_required, medical_staff_required,
    admin_or_manager_required, has_permission, has_app_access
)
from clinic_settings.models import ClinicSettings
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from clinic_system.pagination_utils import paginate_queryset

def generate_barcode_base64(patient_id):
    """Generate a barcode image and return as base64"""
    try:
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(patient_id, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer, {
            'write_text': False,
            'quiet_zone': 2,
            'module_height': 6,
            'module_width': 0.2,
        })
        import base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

@login_required
@app_access_required('patients')
def dashboard(request):
    # Get active tab from URL or default to 'overview'
    active_tab = request.GET.get('tab', 'overview')
    
    # Dashboard statistics - Show all patients for all user roles
    total_patients = Patient.objects.filter(is_active=True).count()
    recent_patients = Patient.objects.filter(is_active=True).order_by('-registration_date')[:10]
    pending_triage = Triage.objects.filter(priority_level__in=['1', '2']).order_by('-triage_date')[:5]
    
    # Add barcode data to recent patients
    for patient in recent_patients:
        patient.barcode_data = generate_barcode_base64(patient.patient_id)
    
    context = {
        'total_patients': total_patients,
        'recent_patients': recent_patients,
        'pending_triage': pending_triage,
        'user_role': request.user.role,
        'active_tab': active_tab,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@app_access_required('patients')
def patient_list(request):
    # Show all active patients for all user roles
    patients = Patient.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Paginate with dynamic page size
    pagination_data = paginate_queryset(request, patients, default_page_size=25)
    
    # Get patient groups for registration modal
    patient_groups = PatientGroup.objects.all()
    
    context = {
        'page_obj': pagination_data['page_obj'],
        'patients': pagination_data['items'],
        'search_query': search_query,
        'user_role': request.user.role,
        'page_size': pagination_data['page_size'],
        'query_string': pagination_data['query_string'],
        'patient_groups': patient_groups,
    }
    return render(request, 'patients/patient_list.html', context)

def generate_barcode(patient_id):
    """Generate a barcode image for the patient ID"""
    # Create a Code128 barcode
    code128 = barcode.get_barcode_class('code128')
    
    # Generate the barcode
    barcode_instance = code128(patient_id, writer=ImageWriter())
    
    # Create a BytesIO buffer to save the image
    buffer = BytesIO()
    
    # Write the barcode to the buffer
    barcode_instance.write(buffer, {
        'write_text': False,  # Don't write the text below the barcode
        'quiet_zone': 2,      # Add some padding around the barcode
        'module_height': 6,   # Height of the barcode
        'module_width': 0.2,  # Width of the thinnest bar
    })
    
    # Convert to base64 for embedding in HTML
    import base64
    barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{barcode_base64}'

@login_required
@app_access_required('patients')
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    user = request.user
    
    # Get vital signs (last 10 records)
    vital_signs = VitalSigns.objects.filter(patient=patient).select_related('recorded_by').order_by('-recorded_date')[:10]
    
    # Get recent appointments (last 5 upcoming or recent)
    try:
        from appointments.models import Appointment, Service
        appointments = Appointment.objects.filter(patient=patient).select_related('provider', 'service', 'created_by')\
            .order_by('-appointment_date', '-appointment_time')[:5]
        # Get active services for appointment scheduling
        services = Service.objects.filter(is_active=True).order_by('category', 'name')
    except ImportError:
        appointments = []
        services = []
    
    # Get recent documents - only if user has medical records access
    documents = []
    if has_app_access(user, 'medical_records'):
        try:
            from medical_records.models import Document
            documents = Document.objects.filter(patient=patient).order_by('-uploaded_at')[:5]
        except ImportError:
            pass
    
    # Get triage records (last 5)
    triages = Triage.objects.filter(patient=patient)\
        .select_related('triaged_by').order_by('-triage_date')[:5]
    
    # Get assessments - filter based on user role
    if user.role in ['doctor', 'physiotherapist', 'nutritionist', 'nurse', 'clinical_assistant', 'medical_director', 'admin']:
        assessments = Assessment.objects.filter(patient=patient)\
            .select_related('assessed_by').order_by('-assessment_date')[:5]
    else:
        assessments = []  # Non-clinical staff can't see assessments
    
    # Get billing information (invoices & payments) - only if user has billing access
    invoices = []
    draft_invoices = []
    payments = []
    if has_app_access(user, 'billing'):
        try:
            from billing.models import Invoice, Payment
            invoices = Invoice.objects.filter(patient=patient).order_by('-issue_date')[:5]
            # Get draft invoices separately for easy access
            draft_invoices = Invoice.objects.filter(patient=patient, status='draft').order_by('-created_at')
            payments = Payment.objects.filter(patient=patient).select_related('invoice', 'processed_by').order_by('-payment_date')[:10]
        except ImportError:
            pass
    
    # Generate barcode for the patient
    barcode_data = generate_barcode(patient.patient_id)
    
    # Get clinic settings for header
    try:
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    # Get medical staff for appointment providers
    User = get_user_model()
    providers = User.objects.filter(
        is_active=True,
        role__in=['doctor', 'physiotherapist', 'nutritionist']
    ).order_by('first_name', 'last_name')
    
    # Laboratory Results and Requests - only if user has lab access
    lab_results = []
    lab_requests = []
    available_lab_tests = []
    if has_app_access(user, 'laboratory'):
        try:
            from laboratory.models import LabTestResult, LabTestRequest, LabTest
            lab_results = LabTestResult.objects.filter(request__patient=patient).select_related('request__test', 'reported_by').order_by('-date_reported')[:10]
            lab_requests = LabTestRequest.objects.filter(patient=patient).select_related('test', 'requested_by').order_by('-date_requested')[:10]
            available_lab_tests = LabTest.objects.filter(is_active=True).order_by('category', 'name')
        except ImportError:
            pass

    # Prescriptions - only if user has pharmacy access
    prescriptions = []
    medications = []
    if has_app_access(user, 'pharmacy'):
        try:
            from pharmacy.models import Prescription, Medication
            prescriptions = Prescription.objects.filter(patient=patient)\
                .select_related('medication', 'prescribed_by', 'dispensed_by')\
                .order_by('-prescribed_date')[:10]
            # Get medications for prescription form
            medications = Medication.objects.filter(is_active=True).order_by('name')
        except ImportError:
            pass

    # Assessment Prescriptions for this patient (assuming prescriptions are stored in Assessment model's treatment_plan or a related model)
    # If you have a separate Prescription model, replace this logic accordingly
    assessment_prescriptions = []
    for assessment in assessments:
        if hasattr(assessment, 'treatment_plan') and assessment.treatment_plan:
            assessment_prescriptions.append({
                'date': assessment.assessment_date,
                'prescribed_by': assessment.assessed_by,
                'text': assessment.treatment_plan,
            })

    # Get active patient groups for the edit form
    patient_groups = PatientGroup.objects.filter(is_active=True).order_by('name')
    
    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'triages': triages,
        'assessments': assessments,
        'appointments': appointments,
        'documents': documents,
        'invoices': invoices,
        'draft_invoices': draft_invoices,
        'payments': payments,
        'barcode_data': barcode_data,
        'active_tab': 'overview',
        'lab_results': lab_results,
        'lab_requests': lab_requests,
        'available_lab_tests': available_lab_tests,
        'prescriptions': prescriptions,
        'medications': medications,
        'assessment_prescriptions': assessment_prescriptions,
        'clinic_settings': clinic_settings,
        'services': services,
        'providers': providers,
        'patient_groups': patient_groups,
    }
    return render(request, 'patients/patient_detail_new.html', context)

@login_required
@permission_required('patients', 'create')
def patient_register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            
            # Generate unique patient ID - get the highest existing ID number
            max_id = 0
            for p in Patient.objects.filter(patient_id__startswith='PT-'):
                try:
                    id_num = int(p.patient_id.split('-')[1])
                    if id_num > max_id:
                        max_id = id_num
                except (ValueError, IndexError):
                    continue
            
            # Generate new ID
            patient.patient_id = f"PT-{max_id + 1:06d}"
            patient.save()
            messages.success(request, f'Patient {patient.get_full_name()} registered successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm()
    
    return render(request, 'patients/patient_register.html', {'form': form})


@login_required
@permission_required('patients', 'create')
def patient_register_ajax(request):
    """AJAX-only quick patient registration from dashboard modal."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    form = PatientForm(request.POST)
    if form.is_valid():
        patient = form.save(commit=False)
        patient.registered_by = request.user

        max_id = 0
        for p in Patient.objects.filter(patient_id__startswith='PT-'):
            try:
                id_num = int(p.patient_id.split('-')[1])
                if id_num > max_id:
                    max_id = id_num
            except (ValueError, IndexError):
                continue

        patient.patient_id = f"PT-{max_id + 1:06d}"
        patient.save()

        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': f'Patient {patient.get_full_name()} ({patient.patient_id}) registered successfully!',
            'patient_id': patient.patient_id,
            'redirect_url': reverse('patients:patient_detail', kwargs={'patient_id': patient.patient_id}),
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@permission_required('patients', 'create')
def visiting_patient_register(request):
    if request.method == 'POST':
        form = VisitingPatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.is_visiting_patient = True
            
            # Generate unique visiting patient ID - get the highest existing ID number
            max_id = 0
            for p in Patient.objects.filter(patient_id__startswith='VP-'):
                try:
                    id_num = int(p.patient_id.split('-')[1])
                    if id_num > max_id:
                        max_id = id_num
                except (ValueError, IndexError):
                    continue
            
            # Generate new ID
            patient.patient_id = f"VP-{max_id + 1:06d}"
            patient.save()
            messages.success(request, f'Visiting patient {patient.patient_id} registered successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = VisitingPatientForm()
    
    return render(request, 'patients/visiting_patient_register.html', {'form': form})

@medical_staff_required
def record_vitals(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = VitalSignsForm(request.POST)
        if form.is_valid():
            vital_signs = form.save(commit=False)
            vital_signs.patient = patient
            vital_signs.recorded_by = request.user
            vital_signs.save()
            messages.success(request, 'Vital signs recorded successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = VitalSignsForm()
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'patients/record_vitals.html', context)

@medical_staff_required
def record_lab_tests(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        from .forms import LabTestForm
        form = LabTestForm(request.POST)
        if form.is_valid():
            lab_test = form.save(commit=False)
            lab_test.patient = patient
            lab_test.recorded_by = request.user
            lab_test.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Laboratory tests recorded successfully!'})
            
            messages.success(request, 'Laboratory tests recorded successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please correct the errors in the form.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@medical_staff_required
def triage_patient(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = TriageForm(request.POST)
        if form.is_valid():
            triage = form.save(commit=False)
            triage.patient = patient
            triage.triaged_by = request.user
            triage.save()
            messages.success(request, 'Patient triage completed successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = TriageForm()
    
    # Get previous triage records for the template
    previous_triages = patient.triages.all()[:5]
    
    context = {
        'form': form,
        'patient': patient,
        'previous_triages': previous_triages,
    }
    return render(request, 'patients/triage.html', context)

@medical_staff_required
def assessment_create(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Determine department from URL parameter or user role
    department = request.GET.get('department')
    if not department:
        # Default based on user role
        if request.user.role == 'doctor':
            department = 'physiotherapy'
        elif request.user.role == 'nutritionist':
            department = 'nutrition'
        else:
            department = 'general'
    
    # Select appropriate form based on department
    if department == 'physiotherapy':
        FormClass = PhysiotherapyAssessmentForm
        template_name = 'patients/physiotherapy_assessment.html'
    elif department == 'nutrition':
        FormClass = NutritionAssessmentForm
        template_name = 'patients/nutrition_assessment.html'
    else:
        FormClass = AssessmentForm
        template_name = 'patients/assessment.html'
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.patient = patient
            assessment.assessed_by = request.user
            assessment.department = department
            assessment.save()
            messages.success(request, f'{department.title()} assessment completed successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
        else:
            # Add error message for debugging
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = FormClass()
        # Pre-populate department
        form.initial['department'] = department
        
        # Pre-populate related_triage if this is a first visit and there's a recent triage
        recent_triage = patient.triages.order_by('-triage_date').first()
        if recent_triage:
            form.initial['related_triage'] = recent_triage.id
            form.initial['chief_complaint'] = recent_triage.chief_complaint
            form.initial['assessment_type'] = 'first_visit'  # Set default assessment type
        else:
            form.initial['assessment_type'] = 'follow_up'  # Default for no triage
    
    # Get available triages for linking
    available_triages = patient.triages.order_by('-triage_date')[:10]
    
    # Get previous assessments for the template
    previous_assessments = patient.assessments.all()[:5]
    
    context = {
        'form': form,
        'patient': patient,
        'available_triages': available_triages,
        'previous_assessments': previous_assessments,
        'department': department,
    }
    return render(request, template_name, context)

@medical_staff_required
def physiotherapy_assessment(request, patient_id):
    """Dedicated physiotherapy assessment view"""
    # Simulate department parameter by modifying request
    request.GET = request.GET.copy()
    request.GET['department'] = 'physiotherapy'
    return assessment_create(request, patient_id)

@medical_staff_required
def nutrition_assessment(request, patient_id):
    """Dedicated nutrition assessment view"""
    # Simulate department parameter by modifying request
    request.GET = request.GET.copy()
    request.GET['department'] = 'nutrition'
    return assessment_create(request, patient_id)

# Legacy view - keep for backward compatibility
@medical_staff_required
def triage_assessment(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = TriageAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.patient = patient
            assessment.assessed_by = request.user
            assessment.save()
            messages.success(request, 'Triage assessment completed successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = TriageAssessmentForm()
    
    # Get previous assessments for the template
    previous_assessments = patient.triage_assessments.all()[:5]
    
    context = {
        'form': form,
        'patient': patient,
        'previous_assessments': previous_assessments,
    }
    return render(request, 'patients/triage_assessment.html', context)

@login_required
@app_access_required('patients')
def patient_details_print(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Get clinic settings for header
    clinic_settings = ClinicSettings.get_settings()
    
    # Get recent vital signs and triage assessments
    vital_signs = patient.vital_signs.order_by('-recorded_date')[:5]
    triage_assessments = patient.triage_assessments.order_by('-assessment_date')[:3]
    
    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'triage_assessments': triage_assessments,
        'clinic_settings': clinic_settings,
    }
    return render(request, 'patients/patient_details_print.html', context)


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    context_object_name = 'patient'

    def get_modal_redirect_url(self):
        return f"{reverse_lazy('patients:patient_detail', kwargs={'patient_id': self.object.patient_id})}?open_modal=patient_update"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return redirect(self.get_modal_redirect_url())
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Patient {self.object.get_full_name()} updated successfully!',
                'redirect_url': self.get_success_url()
            })
        
        return response
    
    def form_invalid(self, form):
        # Handle AJAX request for errors
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })

        messages.error(self.request, 'Please correct the errors in the patient update form and try again.')
        return redirect(self.get_modal_redirect_url())
    
    def get_success_url(self):
        return reverse_lazy('patients:patient_detail', kwargs={'patient_id': self.object.patient_id})
    
    def get_queryset(self):
        return Patient.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update {self.object.get_full_name()}\'s Profile'
        return context


@login_required
@app_access_required('medical_records')
def patient_medical_records(request, patient_id):
    """View for displaying a patient's medical records."""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    vital_signs = patient.vital_signs.order_by('-recorded_date').all()
    triages = patient.triages.order_by('-triage_date').all()
    assessments = patient.assessments.order_by('-assessment_date').all()
    # Keep legacy for backward compatibility
    triage_assessments = patient.triage_assessments.order_by('-assessment_date').all()
    
    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'triages': triages,
        'assessments': assessments,
    }
    return render(request, 'patients/medical_records.html', context)


# =============================================================================
# DEPRECATED: Specialized assessment views removed (Nov 2, 2025)
# All assessments now use the unified general_assessment_ajax() function below
# See ASSESSMENT_SYSTEM_RESTRUCTURE.md for complete documentation
# =============================================================================

@medical_staff_required
def general_assessment_ajax(request, patient_id):
    """AJAX-only general assessment view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    form = AssessmentForm(request.POST)
    
    if form.is_valid():
        assessment = form.save(commit=False)
        assessment.patient = patient
        assessment.assessed_by = request.user
        # Set department from form or default to general
        if not assessment.department:
            assessment.department = 'general'
        
        # Link to appointment if provided
        appointment_id = request.POST.get('appointment_id')
        if appointment_id:
            try:
                from appointments.models import Appointment
                appointment = Appointment.objects.get(id=appointment_id, patient=patient)
                assessment.related_appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        assessment.save()
        
        # Handle follow-up appointment creation
        appointment_created = False
        appointment_details = None
        follow_up_required = request.POST.get('follow_up_required') == 'on'
        follow_up_date = request.POST.get('follow_up_date')
        follow_up_time_str = request.POST.get('follow_up_time', '')
        follow_up_instructions = request.POST.get('follow_up_instructions', '')
        
        # Debug logging
        print(f"[DEBUG] Follow-up Debug Info:")
        print(f"[DEBUG] follow_up_required checkbox: {request.POST.get('follow_up_required')}")
        print(f"[DEBUG] follow_up_required (boolean): {follow_up_required}")
        print(f"[DEBUG] follow_up_date: {follow_up_date}")
        print(f"[DEBUG] follow_up_time: {follow_up_time_str}")
        print(f"[DEBUG] follow_up_instructions: {follow_up_instructions}")
        
        if follow_up_required and follow_up_date:
            try:
                # Parse follow-up time or use default
                if follow_up_time_str:
                    try:
                        follow_up_time = datetime.strptime(follow_up_time_str, '%H:%M').time()
                    except ValueError:
                        follow_up_time = time(9, 0)  # Default to 9:00 AM
                else:
                    follow_up_time = time(9, 0)  # Default to 9:00 AM
                
                # Get or create a general consultation service
                service, created = Service.objects.get_or_create(
                    name='General Follow-up Consultation',
                    category='consultation',
                    defaults={
                        'description': 'Follow-up general medical consultation',
                        'duration_minutes': 30,
                        'base_price': 0.00
                    }
                )
                
                # Create the appointment
                print(f"[DEBUG] Creating appointment with:")
                print(f"[DEBUG] - Patient: {patient}")
                print(f"[DEBUG] - Service: {service.name}")
                print(f"[DEBUG] - Date: {follow_up_date}")
                print(f"[DEBUG] - Time: {follow_up_time}")
                
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=request.user,
                    appointment_date=follow_up_date,
                    appointment_time=follow_up_time,
                    duration_minutes=service.duration_minutes,
                    status='scheduled',
                    notes=f"Follow-up from assessment: {follow_up_instructions}" if follow_up_instructions else "Follow-up appointment from general assessment",
                    created_by=request.user
                )
                appointment_created = True
                print(f"[DEBUG] ✓ Appointment created successfully! ID: {appointment.id}")
                
                appointment_details = {
                    'date': appointment.appointment_date.strftime('%B %d, %Y'),
                    'time': appointment.appointment_time.strftime('%I:%M %p'),
                    'service': appointment.service.name
                }
            except Exception as e:
                # Log the error but don't fail the assessment
                import traceback
                print(f"[ERROR] Failed to create follow-up appointment: {e}")
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                appointment_details = None
        
        response_data = {
            'success': True,
            'message': 'Assessment completed successfully!',
            'assessment_id': assessment.id,
            'appointment_created': appointment_created
        }
        
        if appointment_created and appointment_details:
            response_data['appointment_details'] = appointment_details
        
        return JsonResponse(response_data)
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

@medical_staff_required
def physiotherapy_assessment_ajax(request, patient_id):
    """AJAX-only physiotherapy assessment view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    form = AssessmentForm(request.POST)
    
    if form.is_valid():
        assessment = form.save(commit=False)
        assessment.patient = patient
        assessment.assessed_by = request.user
        assessment.department = 'physiotherapy'
        
        # Link to appointment if provided
        appointment_id = request.POST.get('appointment_id')
        if appointment_id:
            try:
                from appointments.models import Appointment
                appointment = Appointment.objects.get(id=appointment_id, patient=patient)
                assessment.related_appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        assessment.save()
        
        # Handle follow-up appointment creation
        appointment_created = False
        follow_up_required = request.POST.get('follow_up_required') == 'on'
        follow_up_date = request.POST.get('follow_up_date')
        follow_up_instructions = request.POST.get('follow_up_instructions', '')
        
        if follow_up_required and follow_up_date:
            try:
                # Get or create a physiotherapy follow-up service
                service, created = Service.objects.get_or_create(
                    name='Physiotherapy Follow-up',
                    category='physiotherapy',
                    defaults={
                        'description': 'Follow-up physiotherapy session',
                        'duration_minutes': 60,
                        'base_price': 0.00
                    }
                )
                
                # Create the appointment
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=request.user,
                    appointment_date=follow_up_date,
                    appointment_time=datetime.now().time(),
                    duration_minutes=service.duration_minutes,
                    status='scheduled',
                    notes=f"Follow-up from assessment: {follow_up_instructions}" if follow_up_instructions else "Follow-up appointment from physiotherapy assessment"
                )
                appointment_created = True
            except Exception as e:
                # Log the error but don't fail the assessment
                print(f"Error creating follow-up appointment: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Physiotherapy assessment completed successfully!',
            'assessment_id': assessment.id,
            'appointment_created': appointment_created
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

@medical_staff_required
def nutrition_assessment_ajax(request, patient_id):
    """AJAX-only nutrition assessment view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    form = AssessmentForm(request.POST)
    
    if form.is_valid():
        assessment = form.save(commit=False)
        assessment.patient = patient
        assessment.assessed_by = request.user
        assessment.department = 'nutrition'
        
        # Link to appointment if provided
        appointment_id = request.POST.get('appointment_id')
        if appointment_id:
            try:
                from appointments.models import Appointment
                appointment = Appointment.objects.get(id=appointment_id, patient=patient)
                assessment.related_appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        assessment.save()
        
        # Handle follow-up appointment creation
        appointment_created = False
        follow_up_required = request.POST.get('follow_up_required') == 'on'
        follow_up_date = request.POST.get('follow_up_date')
        follow_up_instructions = request.POST.get('follow_up_instructions', '')
        
        if follow_up_required and follow_up_date:
            try:
                # Get or create a nutrition follow-up service
                service, created = Service.objects.get_or_create(
                    name='Nutrition Follow-up',
                    category='nutrition',
                    defaults={
                        'description': 'Follow-up nutrition consultation',
                        'duration_minutes': 45,
                        'base_price': 0.00
                    }
                )
                
                # Create the appointment
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=request.user,
                    appointment_date=follow_up_date,
                    appointment_time=datetime.now().time(),
                    duration_minutes=service.duration_minutes,
                    status='scheduled',
                    notes=f"Follow-up from assessment: {follow_up_instructions}" if follow_up_instructions else "Follow-up appointment from nutrition assessment"
                )
                appointment_created = True
            except Exception as e:
                # Log the error but don't fail the assessment
                print(f"Error creating follow-up appointment: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Nutrition assessment completed successfully!',
            'assessment_id': assessment.id,
            'appointment_created': appointment_created
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
@medical_staff_required
def physiotherapist_patients(request):
    """
    Comprehensive view for physiotherapists to see ALL patients in the physiotherapy department:
    - Patients currently in the physiotherapy department (via triage)
    - Patients with physiotherapy assessments (by any physiotherapist)
    - Patients with physiotherapy appointments
    - Patients previously worked on in the department
    """
    # Check if user is a doctor/physiotherapist
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. This page is only for physiotherapists.')
        return redirect('patients:dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-last_assessment')
    view_type = request.GET.get('view', 'all')  # 'all' or 'my_patients'
    
    # Get ALL patients in the entire system (not just physiotherapy)
    all_patients = Patient.objects.filter(is_active=True).distinct()
    
    # Get MY patients (only those I've worked with or have appointments with)
    my_patients = Patient.objects.filter(
        Q(assessments__assessed_by=request.user) |
        Q(appointments__provider=request.user),
        is_active=True
    ).distinct()
    
    # Choose which patient set to display based on view_type
    if view_type == 'my_patients':
        patients = my_patients
    else:
        patients = all_patients
    
    # Debug: Show initial patient count
    initial_count = patients.count()
    if initial_count == 0:
        messages.warning(request, 'No patients found in physiotherapy department. Please ensure patients have been triaged to physiotherapy or have physiotherapy assessments/appointments.')
    
    # Apply search filter
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Annotate patients with additional data (all assessments and appointments)
    from django.db.models import Count, Max, Prefetch, Q as QFilter
    
    patients = patients.annotate(
        assessment_count=Count('assessments', distinct=True),
        last_assessment_date=Max('assessments__assessment_date'),
        appointment_count=Count('appointments', distinct=True)
    )
    
    # Apply status filter
    if status_filter == 'active':
        # Patients with upcoming appointments or recent assessments (within 30 days)
        from datetime import timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        patients = patients.filter(
            Q(appointments__status__in=['scheduled', 'confirmed', 'in_progress'],
              appointments__appointment_date__gte=timezone.now().date()) |
            Q(assessments__assessment_date__gte=thirty_days_ago)
        ).distinct()
    elif status_filter == 'follow_up':
        # Patients requiring follow-up
        patients = patients.filter(
            assessments__follow_up_required=True,
            assessments__follow_up_date__gte=datetime.now().date()
        ).distinct()
    elif status_filter == 'completed':
        # Patients with completed appointments
        patients = patients.filter(
            appointments__status='completed'
        ).distinct()
    # If status_filter is 'all', don't apply any additional filtering - show all patients
    
    # Debug: Show filtered patient count
    filtered_count = patients.count()
    if status_filter != 'all' and filtered_count < initial_count:
        messages.info(request, f'Showing {filtered_count} patients with "{status_filter}" status. Change filter to "All Patients" to see all {initial_count} patients.')
    
    # Apply sorting (with fallback to ensure consistent ordering)
    if sort_by == '-last_assessment':
        patients = patients.order_by('-last_assessment_date', 'id')
    elif sort_by == 'name':
        patients = patients.order_by('first_name', 'last_name', 'id')
    elif sort_by == '-assessment_count':
        patients = patients.order_by('-assessment_count', 'id')
    else:
        patients = patients.order_by('id')  # Default ordering
    
    # Prefetch related data for efficiency (all patient data)
    patients = patients.prefetch_related(
        Prefetch('assessments', queryset=Assessment.objects.all().order_by('-assessment_date')),
        Prefetch('appointments', queryset=Appointment.objects.all().order_by('-appointment_date')),
        'vital_signs',
        'triages'
    )
    
    # Debug: Log the actual query and count before pagination
    final_count = patients.count()
    print(f"DEBUG: Final patient count before pagination: {final_count}")
    print(f"DEBUG: Status filter: {status_filter}")
    print(f"DEBUG: Sort by: {sort_by}")
    print(f"DEBUG: Search query: {search_query}")
    
    # Show debug info to user
    if view_type == 'my_patients':
        messages.info(request, f'Showing {final_count} of your patients.')
    else:
        messages.info(request, f'Showing {final_count} total patients in the system.')
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics (physiotherapy department only)
    total_patients = patients.count()
    total_assessments = Assessment.objects.filter(department='physiotherapy').count()
    total_appointments = Appointment.objects.filter(service__category='physiotherapy').count()
    
    # Upcoming appointments (physiotherapy appointments only)
    upcoming_appointments = Appointment.objects.filter(
        service__category='physiotherapy',
        status__in=['scheduled', 'confirmed'],
        appointment_date__gte=datetime.now().date()
    ).select_related('patient', 'provider', 'service').order_by('appointment_date', 'appointment_time')[:10]
    
    # Patients requiring follow-up (physiotherapy patients)
    follow_up_patients = Patient.objects.filter(
        assessments__department='physiotherapy',
        assessments__follow_up_required=True,
        assessments__follow_up_date__gte=datetime.now().date()
    ).distinct().count()
    
    context = {
        'page_obj': page_obj,
        'patients': page_obj,
        'total_patients': total_patients,
        'total_assessments': total_assessments,
        'total_appointments': total_appointments,
        'follow_up_patients': follow_up_patients,
        'upcoming_appointments': upcoming_appointments,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'view_type': view_type,
        'all_patients_count': all_patients.count(),
        'my_patients_count': my_patients.count(),
    }
    
    return render(request, 'patients/physiotherapist_patients.html', context)

@login_required
@medical_staff_required
def nutritionist_patients(request):
    """
    Comprehensive view for nutritionists to see ALL patients in the clinic:
    - All patients in the system
    - Patients with nutrition assessments
    - Patients with nutrition appointments
    - Patients previously worked on by the nutritionist
    """
    # Check if user is a nutritionist
    if request.user.role != 'nutritionist':
        messages.error(request, 'Access denied. This page is only for nutritionists.')
        return redirect('patients:dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-last_assessment')
    view_type = request.GET.get('view', 'all')  # 'all' or 'my_patients'
    
    # Get ALL patients in the entire system
    all_patients = Patient.objects.filter(is_active=True).distinct()
    
    # Get MY patients (only those I've worked with or have appointments with)
    my_patients = Patient.objects.filter(
        Q(assessments__assessed_by=request.user) |
        Q(appointments__provider=request.user),
        is_active=True
    ).distinct()
    
    # Choose which patient set to display based on view_type
    if view_type == 'my_patients':
        patients = my_patients
    else:
        patients = all_patients
    
    # Debug: Show initial patient count
    initial_count = patients.count()
    if initial_count == 0:
        messages.warning(request, 'No patients found. Please ensure patients are registered in the system.')
    
    # Apply search filter
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Annotate patients with additional data (all assessments and appointments)
    from django.db.models import Count, Max, Prefetch, Q as QFilter
    
    patients = patients.annotate(
        assessment_count=Count('assessments', distinct=True),
        last_assessment_date=Max('assessments__assessment_date'),
        appointment_count=Count('appointments', distinct=True)
    )
    
    # Apply status filter
    if status_filter == 'active':
        # Patients with upcoming appointments or recent assessments (within 30 days)
        from datetime import timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        patients = patients.filter(
            Q(appointments__status__in=['scheduled', 'confirmed', 'in_progress'],
              appointments__appointment_date__gte=timezone.now().date()) |
            Q(assessments__assessment_date__gte=thirty_days_ago)
        ).distinct()
    elif status_filter == 'follow_up':
        # Patients requiring follow-up
        patients = patients.filter(
            assessments__follow_up_required=True,
            assessments__follow_up_date__gte=datetime.now().date()
        ).distinct()
    elif status_filter == 'completed':
        # Patients with completed appointments
        patients = patients.filter(
            appointments__status='completed'
        ).distinct()
    
    # Debug: Show filtered patient count
    filtered_count = patients.count()
    if status_filter != 'all' and filtered_count < initial_count:
        messages.info(request, f'Showing {filtered_count} patients with "{status_filter}" status. Change filter to "All Patients" to see all {initial_count} patients.')
    
    # Apply sorting (with fallback to ensure consistent ordering)
    if sort_by == '-last_assessment':
        patients = patients.order_by('-last_assessment_date', 'id')
    elif sort_by == 'name':
        patients = patients.order_by('first_name', 'last_name', 'id')
    elif sort_by == '-assessment_count':
        patients = patients.order_by('-assessment_count', 'id')
    else:
        patients = patients.order_by('id')  # Default ordering
    
    # Prefetch related data for efficiency (all patient data)
    patients = patients.prefetch_related(
        Prefetch('assessments', queryset=Assessment.objects.all().order_by('-assessment_date')),
        Prefetch('appointments', queryset=Appointment.objects.all().order_by('-appointment_date')),
        'vital_signs',
        'triages'
    )
    
    # Debug: Log the actual query and count before pagination
    final_count = patients.count()
    
    # Show debug info to user
    if view_type == 'my_patients':
        messages.info(request, f'Showing {final_count} of your patients.')
    else:
        messages.info(request, f'Showing {final_count} total patients in the system.')
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics (nutrition department only)
    total_patients = patients.count()
    total_assessments = Assessment.objects.filter(department='nutrition').count()
    total_appointments = Appointment.objects.filter(service__category='nutrition').count()
    
    # Upcoming appointments (nutrition appointments only)
    upcoming_appointments = Appointment.objects.filter(
        service__category='nutrition',
        status__in=['scheduled', 'confirmed'],
        appointment_date__gte=datetime.now().date()
    ).select_related('patient', 'provider', 'service').order_by('appointment_date', 'appointment_time')[:10]
    
    # Patients requiring follow-up (nutrition patients)
    follow_up_patients = Patient.objects.filter(
        assessments__department='nutrition',
        assessments__follow_up_required=True,
        assessments__follow_up_date__gte=datetime.now().date()
    ).distinct().count()
    
    context = {
        'page_obj': page_obj,
        'patients': page_obj,
        'total_patients': total_patients,
        'total_assessments': total_assessments,
        'total_appointments': total_appointments,
        'follow_up_patients': follow_up_patients,
        'upcoming_appointments': upcoming_appointments,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'view_type': view_type,
        'all_patients_count': all_patients.count(),
        'my_patients_count': my_patients.count(),
    }
    
    return render(request, 'patients/nutritionist_patients.html', context)


# ==================== AJAX-ONLY VIEWS ====================

@login_required
@medical_staff_required
def vital_signs_record_ajax(request, patient_id):
    """AJAX-only vital signs recording view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    form = VitalSignsForm(request.POST)
    if form.is_valid():
        vital_signs = form.save(commit=False)
        vital_signs.patient = patient
        vital_signs.recorded_by = request.user
        vital_signs.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': f'Vital signs for {patient.get_full_name()} recorded successfully!',
            'vital_id': vital_signs.id,
            'redirect_url': reverse('patients:patient_detail', kwargs={'patient_id': patient.patient_id})
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
@medical_staff_required
def triage_create_ajax(request, patient_id):
    """AJAX-only triage creation view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    form = TriageForm(request.POST)
    if form.is_valid():
        triage = form.save(commit=False)
        triage.patient = patient
        triage.triaged_by = request.user
        triage.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': f'Triage for {patient.get_full_name()} completed successfully!',
            'triage_id': triage.id,
            'redirect_url': reverse('patients:patient_detail', kwargs={'patient_id': patient.patient_id})
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
@medical_staff_required
def vital_signs_get_ajax(request, vital_id):
    """AJAX endpoint to get a single vital signs record as JSON for editing"""
    vital = get_object_or_404(VitalSigns, pk=vital_id)
    data = {
        'id': vital.id,
        'height': str(vital.height),
        'weight': str(vital.weight),
        'blood_pressure_systolic': vital.blood_pressure_systolic,
        'blood_pressure_diastolic': vital.blood_pressure_diastolic,
        'heart_rate': vital.heart_rate,
        'temperature': str(vital.temperature),
        'respiratory_rate': vital.respiratory_rate,
        'oxygen_saturation': vital.oxygen_saturation,
        'eyes_rt': vital.eyes_rt,
        'eyes_lt': vital.eyes_lt,
        'ears_rt': vital.ears_rt,
        'ears_lt': vital.ears_lt,
        'cardiovascular': vital.cardiovascular,
        'heart': vital.heart,
        'lungs': vital.lungs,
        'chest_xray': vital.chest_xray,
        'respiratory_exam': vital.respiratory_exam,
        'gi_abdomen': vital.gi_abdomen,
        'cns': vital.cns,
        'psychiatry': vital.psychiatry,
        'extremities': vital.extremities,
        'skin': vital.skin,
        'deformities': vital.deformities,
        'hernia': vital.hernia,
        'varicose_veins': vital.varicose_veins,
        'venereal_diseases': vital.venereal_diseases,
        'notes': vital.notes,
    }
    return JsonResponse({'success': True, 'data': data})


@login_required
@medical_staff_required
def vital_signs_update_ajax(request, vital_id):
    """AJAX endpoint to update an existing vital signs record"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    vital = get_object_or_404(VitalSigns, pk=vital_id)
    form = VitalSignsForm(request.POST, instance=vital)
    if form.is_valid():
        form.save()
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': 'Vital signs updated successfully!',
            'vital_id': vital.id,
            'redirect_url': reverse('patients:patient_detail', kwargs={'patient_id': vital.patient.patient_id})
        })
    else:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@login_required
@app_access_required('patients')
def download_all_reports(request, patient_id):
    """Download all lab test reports for a patient as a ZIP file (PDF via Playwright)."""
    import zipfile
    import io
    import re
    import logging

    logger = logging.getLogger(__name__)
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)

    try:
        from laboratory.models import LabTestRequest
        qs = LabTestRequest.objects.filter(patient=patient).select_related(
            'patient', 'test', 'test__profile', 'test__category', 'requested_by'
        ).order_by('-date_requested')
        # Optional: filter by specific test IDs passed as ?ids=1,2,3
        ids_param = request.GET.get('ids', '')
        if ids_param:
            try:
                pk_list = [int(x) for x in ids_param.split(',') if x.strip()]
                if pk_list:
                    qs = qs.filter(pk__in=pk_list)
            except ValueError:
                pass
        lab_requests = list(qs)
    except ImportError:
        return JsonResponse({'error': 'Laboratory module not available.'}, status=400)

    if not lab_requests:
        messages.warning(request, 'No lab test reports found for this patient.')
        return redirect('patients:patient_detail', patient_id=patient_id)

    try:
        clinic_settings = ClinicSettings.objects.first()
    except Exception:
        clinic_settings = None

    # Check Playwright availability
    try:
        from playwright.sync_api import sync_playwright
        use_playwright = True
    except ImportError:
        use_playwright = False

    base_url = request.build_absolute_uri('/').rstrip('/')

    # Import the shared helper from laboratory
    from laboratory.views import generate_report_html_for_pdf

    # Pre-load related objects to avoid issues in thread
    for lr in lab_requests:
        _ = lr.patient.get_full_name()
        _ = lr.test.name
        _ = lr.test.category
        if lr.test.profile:
            _ = lr.test.profile.sample_type
        try:
            result = lr.result
            _ = list(result.parameter_results.select_related('parameter', 'parameter__category').all())
        except Exception:
            pass

    safe_patient = re.sub(r'[^\w]', '_', patient.get_full_name()).strip('_') or patient_id

    zip_buffer = io.BytesIO()

    if use_playwright:
        def _generate_pdfs(lr_list, cs, b_url):
            import os
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
            pdfs = []
            from playwright.sync_api import sync_playwright as _sp
            with _sp() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                for lr in lr_list:
                    try:
                        html = generate_report_html_for_pdf(lr, cs, b_url)
                        test_name = re.sub(r'[^\w]', '_', lr.test.name).strip('_')
                        date_str = lr.date_requested.strftime('%Y-%m-%d')
                        fname = f"{test_name}_{date_str}_{lr.pk}.pdf"
                        page.set_content(html)
                        page.wait_for_load_state('networkidle')
                        pdf_bytes = page.pdf(
                            format='A4',
                            print_background=True,
                            margin={'top': '0mm', 'right': '0mm', 'bottom': '10mm', 'left': '0mm'},
                        )
                        pdfs.append((fname, pdf_bytes))
                    except Exception as e:
                        logger.error(f"PDF generation failed for test {lr.pk}: {e}")
                browser.close()
            return pdfs

        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(_generate_pdfs, lab_requests, clinic_settings, base_url)
                pdfs = future.result(timeout=300)

            if not pdfs:
                messages.error(request, 'Could not generate any PDF reports.')
                return redirect('patients:patient_detail', patient_id=patient_id)

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for fname, pdf_bytes in pdfs:
                    zf.writestr(fname, pdf_bytes)

        except Exception as e:
            logger.error(f"Batch PDF generation failed for patient {patient_id}: {e}", exc_info=True)
            messages.error(request, f'Report generation failed: {e}')
            return redirect('patients:patient_detail', patient_id=patient_id)
    else:
        # Fallback: HTML files
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for lr in lab_requests:
                try:
                    html = generate_report_html_for_pdf(lr, clinic_settings, base_url)
                    test_name = re.sub(r'[^\w]', '_', lr.test.name).strip('_')
                    date_str = lr.date_requested.strftime('%Y-%m-%d')
                    fname = f"{test_name}_{date_str}_{lr.pk}.html"
                    zf.writestr(fname, html)
                except Exception as e:
                    logger.error(f"HTML generation failed for test {lr.pk}: {e}")

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{safe_patient}_Lab_Reports.zip"'
    return response
