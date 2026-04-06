"""
Decorators for access control in the clinic system
"""
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


def admin_required(view_func):
    """
    Decorator for views that checks if the user is an administrator.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        
        if request.user.role != 'admin' and not request.user.is_superuser:
            raise PermissionDenied("You must be an administrator to access this page.")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def medical_staff_required(view_func):
    """
    Decorator for views that checks if the user is medical staff (doctor, nurse, nutritionist).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        
        allowed_roles = ['admin', 'doctor', 'nurse', 'nutritionist']
        if request.user.role not in allowed_roles and not request.user.is_superuser:
            raise PermissionDenied("You must be medical staff to access this page.")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Decorator factory for views that checks if the user has one of the specified roles.
    Usage: @role_required('admin', 'doctor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                from django.conf import settings
                return redirect(settings.LOGIN_URL)
            
            if request.user.role not in roles and not request.user.is_superuser:
                raise PermissionDenied(f"You must have one of these roles: {', '.join(roles)}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
