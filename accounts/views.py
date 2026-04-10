from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from .models import User, UserAppPermission, SYSTEM_APPS
from .permissions import get_user_apps, has_app_access, ROLE_PERMISSIONS

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """After login, send users to the main dashboard."""
        return reverse_lazy('dashboard')

def custom_logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

@login_required
def dashboard(request):
    """Main dashboard showing overview of all clinic modules."""
    from patients.models import Patient, PatientGroup
    from appointments.models import Appointment
    from clinic_settings.models import ClinicSettings, EnabledModule
    
    user = request.user
    today = timezone.now().date()
    
    # Get enabled modules
    enabled_modules = list(EnabledModule.objects.filter(is_enabled=True).values_list('module_name', flat=True))
    
    # Get clinic settings
    try:
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    # Statistics
    total_patients = Patient.objects.count()
    new_patients_today = Patient.objects.filter(registration_date=today).count()
    
    # Appointments
    appointments_today = Appointment.objects.filter(appointment_date=today)
    pending_appointments = appointments_today.filter(status='scheduled').count()
    completed_appointments = appointments_today.filter(status='completed').count()
    
    # Recent patients (last 5)
    recent_patients = Patient.objects.order_by('-registration_date')[:5]
    
    # Lab stats (if enabled)
    lab_pending = 0
    lab_completed_today = 0
    if 'laboratory' in enabled_modules:
        try:
            from laboratory.models import LabTestRequest
            lab_pending = LabTestRequest.objects.filter(status__in=['requested', 'sample_collected', 'in_progress']).count()
            lab_completed_today = LabTestRequest.objects.filter(status='completed', updated_at__date=today).count()
        except:
            pass
    
    # Billing stats (if enabled)
    revenue_today = 0
    pending_invoices = 0
    if 'billing' in enabled_modules:
        try:
            from billing.models import Invoice, Payment
            from django.db.models import Sum
            revenue_today = Payment.objects.filter(payment_date__date=today).aggregate(total=Sum('amount'))['total'] or 0
            pending_invoices = Invoice.objects.filter(status='pending').count()
        except:
            pass
    
    # Pharmacy stats (if enabled)
    low_stock_items = 0
    if 'pharmacy' in enabled_modules:
        try:
            from pharmacy.models import Medication
            low_stock_items = Medication.objects.filter(quantity_in_stock__lte=F('reorder_level')).count()
        except:
            pass
    
    # Get patient groups for registration modal
    patient_groups = PatientGroup.objects.all()

    # Data for existing modals (all_modals.html)
    all_services = []
    all_providers = []
    all_patients = Patient.objects.filter(is_active=True).order_by('first_name', 'last_name')
    if 'appointments' in enabled_modules:
        try:
            from appointments.models import Service
            from django.contrib.auth import get_user_model
            User = get_user_model()
            all_services = Service.objects.filter(is_active=True)
            all_providers = User.objects.filter(role__in=['doctor', 'nutritionist', 'physiotherapist'], is_active=True)
        except:
            pass
    
    context = {
        'user': user,
        'clinic_settings': clinic_settings,
        'enabled_modules': enabled_modules,
        'total_patients': total_patients,
        'new_patients_today': new_patients_today,
        'appointments_today': appointments_today,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'recent_patients': recent_patients,
        'lab_pending': lab_pending,
        'lab_completed_today': lab_completed_today,
        'revenue_today': revenue_today,
        'pending_invoices': pending_invoices,
        'low_stock_items': low_stock_items,
        'active_tab': 'overview',
        'pending_triage': [],  # Placeholder for triage data
        'patient_groups': patient_groups,
        'all_patients': all_patients,
        'all_services': all_services,
        'services': all_services,
        'all_providers': all_providers,
        'modal_active_patients': all_patients,
    }
    
    return render(request, 'dashboard/main_dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


def _is_admin(user):
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'admin')


@login_required
@user_passes_test(_is_admin)
def manage_permissions_view(request):
    """List all users with their permission summary for admins to manage"""
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')

    user_data = []
    for u in users:
        overrides = UserAppPermission.objects.filter(user=u)
        blocked = overrides.filter(is_allowed=False).count()
        granted = overrides.filter(is_allowed=True).count()
        user_data.append({
            'user': u,
            'blocked_count': blocked,
            'granted_count': granted,
            'has_overrides': overrides.exists(),
        })

    context = {
        'user_data': user_data,
        'system_apps': SYSTEM_APPS,
    }
    return render(request, 'accounts/manage_permissions.html', context)


@login_required
@user_passes_test(_is_admin)
def edit_user_permissions_view(request, user_id):
    """Edit app permissions for a specific user"""
    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Handle role change
        new_role = request.POST.get('role')
        if new_role and new_role != target_user.role:
            # Validate the role value against flat choices
            valid_roles = [val for group_label, group_choices in User.ROLE_CHOICES for val, _ in group_choices]
            if new_role in valid_roles:
                target_user.role = new_role
                target_user.save(update_fields=['role'])

        for app_code, app_label in SYSTEM_APPS:
            field_value = request.POST.get(f'app_{app_code}')
            # field_value: 'default' = remove override, 'allow' = force allow, 'block' = force block
            if field_value == 'default':
                UserAppPermission.objects.filter(user=target_user, app_name=app_code).delete()
            elif field_value in ('allow', 'block'):
                obj, created = UserAppPermission.objects.update_or_create(
                    user=target_user,
                    app_name=app_code,
                    defaults={
                        'is_allowed': (field_value == 'allow'),
                        'granted_by': request.user,
                    }
                )
        messages.success(request, f'Permissions updated for {target_user.get_full_name()}.')
        return redirect('accounts:manage_permissions')

    # Build permission state for each app
    overrides = {p.app_name: p for p in UserAppPermission.objects.filter(user=target_user)}
    role_perms = ROLE_PERMISSIONS.get(target_user.role, {})
    role_apps = role_perms.get('apps', [])
    role_restricted = role_perms.get('restricted', {})

    app_states = []
    for app_code, app_label in SYSTEM_APPS:
        override = overrides.get(app_code)
        # Determine role default
        if 'all' in role_apps or app_code in role_apps:
            role_default = 'allowed'
        elif app_code in role_restricted:
            role_default = 'limited'
        else:
            role_default = 'blocked'

        if override is not None:
            current = 'allow' if override.is_allowed else 'block'
        else:
            current = 'default'

        app_states.append({
            'code': app_code,
            'label': app_label,
            'role_default': role_default,
            'current': current,
            'override': override,
        })

    context = {
        'target_user': target_user,
        'app_states': app_states,
        'role_display': target_user.get_role_display(),
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'accounts/edit_user_permissions.html', context)
