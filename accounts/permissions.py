"""
Role-based permissions for PhysioNutrition Clinic System
This module defines access control for all system resources based on user roles.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def is_module_enabled(module_name):
    """Check if a module is enabled in system settings"""
    try:
        from clinic_settings.models import EnabledModule
        return EnabledModule.is_module_enabled(module_name)
    except Exception:
        # If there's any error (e.g., table doesn't exist yet), default to enabled
        return True


# ===========================
# PERMISSION MATRICES
# ===========================

# Define which roles can access which apps/modules
ROLE_PERMISSIONS = {
    # Administration & Management - Full Access
    'admin': {
        'apps': ['all'],
        'permissions': ['create', 'read', 'update', 'delete', 'admin'],
    },
    'clinic_manager': {
        'apps': ['patients', 'appointments', 'billing', 'medical_records', 'laboratory', 
                 'pharmacy', 'reports', 'staff_management', 'budget', 'clinic_settings'],
        'permissions': ['create', 'read', 'update', 'delete'],
    },
    'medical_director': {
        'apps': ['patients', 'appointments', 'medical_records', 'laboratory', 'pharmacy', 'reports'],
        'permissions': ['create', 'read', 'update', 'delete'],
    },
    
    # Clinical Staff
    'doctor': {
        'apps': ['patients', 'appointments', 'medical_records', 'laboratory', 'pharmacy'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'billing': ['read'],
            'reports': ['read'],
        }
    },
    'physiotherapist': {
        'apps': ['patients', 'appointments', 'medical_records'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'laboratory': ['read'],
            'billing': ['read'],
        }
    },
    'nutritionist': {
        'apps': ['patients', 'appointments', 'medical_records'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'laboratory': ['read'],
            'billing': ['read'],
        }
    },
    'nurse': {
        'apps': ['patients', 'appointments', 'medical_records'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'laboratory': ['read'],
        }
    },
    'clinical_assistant': {
        'apps': ['patients', 'appointments'],
        'permissions': ['read', 'update'],
        'restricted': {
            'medical_records': ['read'],
        }
    },
    
    # Reception & Front Desk
    'receptionist': {
        'apps': ['patients', 'appointments'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'billing': ['read', 'create'],
            'medical_records': ['read'],
        }
    },
    'front_desk': {
        'apps': ['patients', 'appointments'],
        'permissions': ['create', 'read', 'update'],
    },
    'appointment_coordinator': {
        'apps': ['appointments'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'patients': ['read'],
            'staff_management': ['read'],
        }
    },
    
    # Laboratory
    'lab_technician': {
        'apps': ['laboratory'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'patients': ['read'],
        }
    },
    'lab_manager': {
        'apps': ['laboratory'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'patients': ['read'],
            'reports': ['read'],
        }
    },
    'pathologist': {
        'apps': ['laboratory'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'patients': ['read'],
            'medical_records': ['read'],
        }
    },
    
    # Pharmacy
    # NOTE: Pharmacy roles should NOT have direct access to the patients app
    # (no patient list/detail views), but can still reference patients inside
    # pharmacy workflows (prescriptions, sales records) through internal queries.
    'pharmacist': {
        'apps': ['pharmacy'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            # Keep read-only access to appointments metadata if needed
            'appointments': ['read'],
        }
    },
    'pharmacy_assistant': {
        'apps': ['pharmacy'],
        'permissions': ['create', 'read', 'update'],
    },
    'pharmacy_manager': {
        'apps': ['pharmacy'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'budget': ['read'],
            'reports': ['read'],
        }
    },
    
    # Billing & Finance
    'billing_officer': {
        # Billing officers should ONLY work inside the billing module.
        # They must NOT have access to patient or appointment pages, but
        # billing views can still use Patient/Appointment models internally.
        'apps': ['billing'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {}
    },
    'accountant': {
        'apps': ['billing', 'budget', 'reports'],
        'permissions': ['create', 'read', 'update', 'delete'],
    },
    'finance_manager': {
        'apps': ['billing', 'budget', 'reports'],
        'permissions': ['create', 'read', 'update', 'delete'],
    },
    'cashier': {
        'apps': ['billing'],
        'permissions': ['create', 'read', 'update'],
    },
    
    # Medical Records
    'medical_records_officer': {
        'apps': ['medical_records'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'patients': ['read'],
        }
    },
    'records_manager': {
        'apps': ['medical_records'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'patients': ['read'],
            'reports': ['read'],
        }
    },
    'data_entry_clerk': {
        'apps': ['medical_records'],
        'permissions': ['create', 'read', 'update'],
    },
    
    # Reports & Analytics
    'reports_analyst': {
        'apps': ['reports'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'all': ['read'],  # Read-only access to all modules for reporting
        }
    },
    'statistician': {
        'apps': ['reports'],
        'permissions': ['create', 'read', 'update'],
        'restricted': {
            'all': ['read'],  # Read-only access to all modules for statistics
        }
    },
    
    # Staff Management
    'hr_manager': {
        'apps': ['staff_management'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'budget': ['read'],
            'reports': ['read'],
        }
    },
    'hr_officer': {
        'apps': ['staff_management'],
        'permissions': ['create', 'read', 'update'],
    },
    
    # Budget & Financial Planning
    'budget_officer': {
        'apps': ['budget'],
        'permissions': ['create', 'read', 'update', 'delete'],
        'restricted': {
            'billing': ['read'],
            'reports': ['read'],
        }
    },
    'financial_controller': {
        'apps': ['budget', 'billing', 'reports'],
        'permissions': ['create', 'read', 'update', 'delete'],
    },
    
    # Support & Maintenance
    'it_support': {
        'apps': ['all'],
        'permissions': ['read'],
        'restricted': {
            'accounts': ['create', 'update', 'delete'],
            'clinic_settings': ['update'],
        }
    },
    'maintenance_staff': {
        'apps': [],
        'permissions': ['read'],
    },
}


# ===========================
# PERMISSION CHECKER FUNCTIONS
# ===========================

def has_app_access(user, app_name):
    """Check if user's role has access to a specific app"""
    if not user.is_authenticated:
        return False
    
    # First check if the module is enabled in system settings
    if not is_module_enabled(app_name):
        return False
    
    role = user.role
    
    # Superusers always have access
    if user.is_superuser:
        return True
    
    # Check per-user overrides (admin-assigned permissions)
    try:
        from .models import UserAppPermission
        override = UserAppPermission.objects.filter(
            user=user, app_name=app_name
        ).first()
        if override is not None:
            return override.is_allowed
    except Exception:
        pass
    
    # Admins have access to everything by default
    if role == 'admin':
        return True
    
    # Fall back to role-based permissions
    role_perms = ROLE_PERMISSIONS.get(role, {})
    allowed_apps = role_perms.get('apps', [])
    restricted_apps = role_perms.get('restricted', {})
    
    # Check if app is in allowed apps or 'all'
    if 'all' in allowed_apps or app_name in allowed_apps:
        return True
    
    # Check if app is in restricted (limited access)
    if app_name in restricted_apps:
        return True
    
    return False


def has_permission(user, app_name, permission):
    """
    Check if user has specific permission for an app
    permission: 'create', 'read', 'update', 'delete', 'admin'
    """
    if not user.is_authenticated:
        return False
    
    role = user.role
    
    # Superusers and admins have all permissions
    if user.is_superuser or role == 'admin':
        return True
    
    role_perms = ROLE_PERMISSIONS.get(role, {})
    
    # Check if permission is in main permissions
    allowed_permissions = role_perms.get('permissions', [])
    if permission in allowed_permissions:
        allowed_apps = role_perms.get('apps', [])
        if 'all' in allowed_apps or app_name in allowed_apps:
            return True
    
    # Check if permission is in restricted (limited permissions)
    restricted_apps = role_perms.get('restricted', {})
    if app_name in restricted_apps:
        return permission in restricted_apps[app_name]
    
    # Special case: reports_analyst and statistician have read access to all
    if role in ['reports_analyst', 'statistician'] and permission == 'read':
        return True
    
    return False


def get_user_apps(user):
    """Get list of apps user has access to"""
    if not user.is_authenticated:
        return []
    
    if user.is_superuser or user.role == 'admin':
        return ['all']
    
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    apps = role_perms.get('apps', [])
    restricted = list(role_perms.get('restricted', {}).keys())
    
    return list(set(apps + restricted))


def get_user_permissions(user, app_name):
    """Get list of permissions user has for a specific app"""
    if not user.is_authenticated:
        return []
    
    if user.is_superuser or user.role == 'admin':
        return ['create', 'read', 'update', 'delete', 'admin']
    
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    
    # Check main permissions
    allowed_apps = role_perms.get('apps', [])
    if 'all' in allowed_apps or app_name in allowed_apps:
        return role_perms.get('permissions', [])
    
    # Check restricted permissions
    restricted_apps = role_perms.get('restricted', {})
    if app_name in restricted_apps:
        return restricted_apps[app_name]
    
    return []


# ===========================
# PERMISSION DECORATORS
# ===========================

def app_access_required(app_name):
    """Decorator to require access to a specific app"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not has_app_access(request.user, app_name):
                messages.error(request, f'You do not have permission to access {app_name.replace("_", " ").title()}.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(app_name, permission):
    """Decorator to require specific permission for an app"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not has_permission(request.user, app_name, permission):
                messages.error(request, f'You do not have permission to {permission} in {app_name.replace("_", " ").title()}.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def medical_staff_required(view_func):
    """Decorator for views that require medical/clinical staff"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        clinical_roles = ['doctor', 'physiotherapist', 'nutritionist', 'nurse', 
                         'clinical_assistant', 'medical_director', 'admin']
        
        if request.user.role not in clinical_roles and not request.user.is_superuser:
            messages.error(request, 'This function is only available to medical staff.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_manager_required(view_func):
    """Decorator for views that require admin or management level access"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        management_roles = ['admin', 'clinic_manager', 'medical_director']
        
        if request.user.role not in management_roles and not request.user.is_superuser:
            messages.error(request, 'This function requires administrative privileges.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def finance_staff_required(view_func):
    """Decorator for views that require finance/billing staff"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        finance_roles = ['billing_officer', 'accountant', 'finance_manager', 'cashier',
                        'clinic_manager', 'admin']
        
        if request.user.role not in finance_roles and not request.user.is_superuser:
            messages.error(request, 'This function is only available to billing/finance staff.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def lab_staff_required(view_func):
    """Decorator for views that require laboratory staff"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        lab_roles = ['lab_technician', 'lab_manager', 'pathologist', 'admin']
        
        if request.user.role not in lab_roles and not request.user.is_superuser:
            messages.error(request, 'This function is only available to laboratory staff.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ===========================
# GRANULAR LAB PERMISSIONS
# ===========================

LAB_ROLES_ALL = ['lab_technician', 'lab_manager', 'pathologist', 'admin']
LAB_ROLES_VERIFY = ['lab_manager', 'pathologist', 'admin']
LAB_ROLES_DELETE = ['lab_manager', 'admin']
LAB_ROLES_MANAGE = ['lab_manager', 'admin']  # manage tests/profiles/parameters


def is_lab_staff(user):
    return user.is_superuser or user.role in LAB_ROLES_ALL


def can_add_result(user):
    """Any lab staff can add results"""
    return is_lab_staff(user)


def can_edit_result(user, result=None):
    """Lab staff can edit results. Technicians can only edit unverified results they reported."""
    if not is_lab_staff(user):
        return False
    if user.is_superuser or user.role in ['lab_manager', 'pathologist', 'admin']:
        return True
    # Technician: only own unverified results
    if result and result.verified:
        return False
    if result and result.reported_by_id != user.pk:
        return False
    return True


def can_verify_result(user):
    """Only lab_manager, pathologist, and admin can verify results"""
    return user.is_superuser or user.role in LAB_ROLES_VERIFY


def can_delete_result(user):
    """Only lab_manager and admin can delete results"""
    return user.is_superuser or user.role in LAB_ROLES_DELETE


def can_manage_lab(user):
    """Only lab_manager and admin can manage tests, profiles, parameters"""
    return user.is_superuser or user.role in LAB_ROLES_MANAGE


def lab_verify_required(view_func):
    """Decorator for views that require result verification privilege"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not can_verify_result(request.user):
            messages.error(request, 'Only Lab Managers and Pathologists can verify results.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def lab_manage_required(view_func):
    """Decorator for views that require lab management privilege (tests/profiles/params)"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not can_manage_lab(request.user):
            messages.error(request, 'Only Lab Managers can manage tests and profiles.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def pharmacy_staff_required(view_func):
    """Decorator for views that require pharmacy staff"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        pharmacy_roles = ['pharmacist', 'pharmacy_assistant', 'pharmacy_manager', 'admin']
        
        if request.user.role not in pharmacy_roles and not request.user.is_superuser:
            messages.error(request, 'This function is only available to pharmacy staff.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ===========================
# PERMISSION CONTEXT PROCESSOR
# ===========================

def user_permissions(request):
    """Context processor to make permissions available in templates"""
    if not request.user.is_authenticated:
        return {
            'user_apps': [],
            'user_permissions': {},
            'is_medical_staff': False,
            'is_admin_or_manager': False,
            'is_finance_staff': False,
        }
    
    user = request.user
    
    # Get all apps user has access to
    user_apps = get_user_apps(user)
    
    # Get permissions for each app
    app_list = ['patients', 'appointments', 'billing', 'medical_records', 'laboratory',
                'pharmacy', 'reports', 'staff_management', 'budget', 'clinic_settings']
    
    user_perms = {}
    for app in app_list:
        user_perms[app] = get_user_permissions(user, app)
    
    # Role category checks
    clinical_roles = ['doctor', 'physiotherapist', 'nutritionist', 'nurse', 
                     'clinical_assistant', 'medical_director', 'admin']
    management_roles = ['admin', 'clinic_manager', 'medical_director']
    finance_roles = ['billing_officer', 'accountant', 'finance_manager', 'cashier',
                    'clinic_manager', 'admin']
    
    return {
        'user_apps': user_apps,
        'user_permissions': user_perms,
        'is_medical_staff': user.role in clinical_roles or user.is_superuser,
        'is_admin_or_manager': user.role in management_roles or user.is_superuser,
        'is_finance_staff': user.role in finance_roles or user.is_superuser,
        'is_lab_staff': user.role in LAB_ROLES_ALL or user.is_superuser,
        'can_verify_lab_result': can_verify_result(user),
        'can_delete_lab_result': can_delete_result(user),
        'can_manage_lab': can_manage_lab(user),
        'is_pharmacy_staff': user.role in ['pharmacist', 'pharmacy_assistant', 'pharmacy_manager', 'admin'] or user.is_superuser,
    }
