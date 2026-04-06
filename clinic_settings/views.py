import os
import shutil
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import Http404, JsonResponse, FileResponse
from django.conf import settings as django_settings
from .models import ClinicSettings, EnabledModule
from .forms import ClinicSettingsForm, ThemeCustomizationForm


def is_admin_or_superuser(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'admin')


@login_required
@user_passes_test(is_admin_or_superuser)
def clinic_settings_view(request):
    """View and edit clinic settings"""
    settings = ClinicSettings.get_settings()
    
    if request.method == 'POST':
        form = ClinicSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clinic settings updated successfully!')
            return redirect('clinic_settings:settings')
    else:
        form = ClinicSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'clinic_settings/settings.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def modules_management_view(request):
    """View for managing enabled/disabled modules"""
    # Initialize modules if they don't exist
    EnabledModule.initialize_modules()
    
    if request.method == 'POST':
        # Get all module checkboxes from form
        for module in EnabledModule.objects.filter(hospital__isnull=True):
            is_enabled = request.POST.get(f'module_{module.module_name}') == 'on'
            if module.is_enabled != is_enabled:
                module.is_enabled = is_enabled
                module.save()
        
        messages.success(request, 'Module settings updated successfully!')
        return redirect('clinic_settings:modules')
    
    modules = EnabledModule.objects.filter(hospital__isnull=True).order_by('order')
    
    context = {
        'modules': modules,
    }
    return render(request, 'clinic_settings/modules.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def toggle_module_ajax(request):
    """AJAX endpoint to toggle a module on/off"""
    if request.method == 'POST':
        module_name = request.POST.get('module_name')
        is_enabled = request.POST.get('is_enabled') == 'true'
        
        try:
            module = EnabledModule.objects.get(module_name=module_name, hospital__isnull=True)
            module.is_enabled = is_enabled
            module.save()
            return JsonResponse({'success': True, 'is_enabled': module.is_enabled})
        except EnabledModule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Module not found'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_admin_or_superuser)
def theme_customization_view(request):
    """View for customizing theme colors"""
    settings = ClinicSettings.get_settings()
    
    if request.method == 'POST':
        if 'reset_defaults' in request.POST:
            # Reset all colors to defaults
            default_colors = {
                # Primary Colors
                'primary_color': '#1B5E96',
                'primary_dark': '#154a7a',
                'primary_light': '#e6f1fa',
                # Success Colors
                'success_color': '#2E8B57',
                'success_dark': '#236b43',
                'success_light': '#e8f5f0',
                # Accent Colors
                'accent_color': '#00A86B',
                'accent_dark': '#008554',
                'accent_light': '#e6f9f3',
                # Warning Colors
                'warning_color': '#FF8C00',
                'warning_dark': '#e67e00',
                'warning_light': '#fff4e6',
                # Danger Colors
                'danger_color': '#dc2626',
                'danger_dark': '#b91c1c',
                'danger_light': '#fecaca',
                # Info Colors
                'info_color': '#0891b2',
                'info_dark': '#0e7490',
                'info_light': '#cffafe',
                # Secondary Colors
                'secondary_color': '#64748b',
                'secondary_dark': '#475569',
                'secondary_light': '#f1f5f9',
                # Base Colors
                'dark_color': '#1e293b',
                'light_color': '#f8fafc',
                'border_color': '#e2e8f0',
                # Text Colors
                'text_primary': '#1e293b',
                'text_secondary': '#64748b',
                'text_muted': '#94a3b8',
                # Background Colors
                'bg_primary': '#ffffff',
                'bg_secondary': '#f8fafc',
                'bg_tertiary': '#f1f5f9',
                # Chart Colors
                'chart_color_1': '#1B5E96',
                'chart_color_2': '#2E8B57',
                'chart_color_3': '#00A86B',
                'chart_color_4': '#FF8C00',
                'chart_color_5': '#0891b2',
                'chart_color_6': '#dc2626',
            }
            
            for field, value in default_colors.items():
                setattr(settings, field, value)
            settings.save()
            messages.success(request, 'Theme colors have been reset to default values!')
            return redirect('clinic_settings:theme_customization')
        else:
            form = ThemeCustomizationForm(request.POST, instance=settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Theme colors updated successfully!')
                return redirect('clinic_settings:theme_customization')
    else:
        form = ThemeCustomizationForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'clinic_settings/theme_customization.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def database_management_view(request):
    """View for database export and import"""
    db_path = django_settings.DATABASES['default']['NAME']
    db_exists = os.path.exists(db_path)
    db_size = os.path.getsize(db_path) if db_exists else 0
    db_modified = datetime.datetime.fromtimestamp(os.path.getmtime(db_path)) if db_exists else None

    # Find backup files
    backup_dir = os.path.join(django_settings.BASE_DIR, 'db_backups')
    backups = []
    if os.path.exists(backup_dir):
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith('.sqlite3'):
                fpath = os.path.join(backup_dir, f)
                backups.append({
                    'name': f,
                    'size': os.path.getsize(fpath),
                    'date': datetime.datetime.fromtimestamp(os.path.getmtime(fpath)),
                })

    context = {
        'db_exists': db_exists,
        'db_size': db_size,
        'db_modified': db_modified,
        'backups': backups[:10],
    }
    return render(request, 'clinic_settings/database_management.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def database_export_view(request):
    """Download the SQLite database file"""
    db_path = django_settings.DATABASES['default']['NAME']
    if not os.path.exists(db_path):
        messages.error(request, 'Database file not found.')
        return redirect('clinic_settings:database')

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'excellence_med_care_backup_{timestamp}.sqlite3'

    response = FileResponse(open(db_path, 'rb'), content_type='application/x-sqlite3')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@user_passes_test(is_admin_or_superuser)
def database_import_view(request):
    """Upload and replace the SQLite database file"""
    if request.method != 'POST':
        return redirect('clinic_settings:database')

    uploaded_file = request.FILES.get('database_file')
    if not uploaded_file:
        messages.error(request, 'No file was uploaded.')
        return redirect('clinic_settings:database')

    if not uploaded_file.name.endswith('.sqlite3'):
        messages.error(request, 'Invalid file type. Please upload a .sqlite3 file.')
        return redirect('clinic_settings:database')

    db_path = str(django_settings.DATABASES['default']['NAME'])

    # Create backup directory
    backup_dir = os.path.join(django_settings.BASE_DIR, 'db_backups')
    os.makedirs(backup_dir, exist_ok=True)

    # Backup current database before replacing
    if os.path.exists(db_path):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'db_before_import_{timestamp}.sqlite3')
        shutil.copy2(db_path, backup_path)

    # Write uploaded file to a temp path first, then replace
    temp_path = db_path + '.tmp'
    try:
        with open(temp_path, 'wb') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        # Basic validation: check it's a real SQLite file
        with open(temp_path, 'rb') as f:
            header = f.read(16)
        if not header.startswith(b'SQLite format 3'):
            os.remove(temp_path)
            messages.error(request, 'The uploaded file is not a valid SQLite database.')
            return redirect('clinic_settings:database')

        # Replace the database
        shutil.move(temp_path, db_path)
        messages.success(request, 'Database imported successfully! A backup of the previous database was saved. Please restart the server for changes to take full effect.')
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        messages.error(request, f'Error importing database: {str(e)}')

    return redirect('clinic_settings:database')
