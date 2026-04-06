from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def medical_staff_required(view_func):
    """
    Decorator that restricts access to medical information entry to only:
    - Doctors/Physiotherapists
    - Nutritionists
    - Administrators
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['doctor', 'nutritionist', 'admin', 'nurse']:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'medical_records/access_denied.html', {
                'message': 'Only medical staff (Doctors, Nurses, Physiotherapists, and Nutritionists) can access medical information.',
                'user_role': request.user.get_role_display()
            }, status=403)
    return _wrapped_view

def can_edit_medical_records(user):
    """
    Helper function to check if user can edit medical records
    """
    return user.role in ['doctor', 'nutritionist', 'admin']

def can_view_medical_records(user):
    """
    Helper function to check if user can view medical records
    Medical records can be viewed by medical staff and nurses
    """
    return user.role in ['doctor', 'nutritionist', 'admin', 'nurse']
