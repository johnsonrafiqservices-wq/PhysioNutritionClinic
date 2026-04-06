"""
Role-based access control middleware for PhysioNutrition Clinic System
This middleware enforces permissions at the URL level to prevent unauthorized access
"""

from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import resolve
from .permissions import has_app_access, has_permission

class RoleBasedAccessMiddleware:
    """
    Middleware to enforce role-based access control for all views.
    Checks if the user has permission to access the requested app/module.
    """
    
    # Map URL namespaces to app names for permission checking
    APP_NAMESPACE_MAP = {
        'patients': 'patients',
        'appointments': 'appointments',
        'billing': 'billing',
        'medical_records': 'medical_records',
        'laboratory': 'laboratory',
        'pharmacy': 'pharmacy',
        'reports': 'reports',
        'staff_management': 'staff_management',
        'budget': 'budget',
        'clinic_settings': 'clinic_settings',
    }
    
    # URLs that don't require permission checks
    EXEMPT_URLS = [
        'login',
        'logout',
        'password_reset',
        'password_reset_done',
        'password_reset_confirm',
        'password_reset_complete',
        'dashboard',
        'home',
        'admin',
        'access_restricted',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.process_request(request)
        if response:
            return response
        
        # Get the response from the next middleware/view
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        """
        Check if the user has permission to access the requested URL.
        Returns a redirect response if access is denied, None otherwise.
        """
        # Skip checks for unauthenticated users (they'll be redirected by login_required)
        if not request.user.is_authenticated:
            return None
        
        # Skip checks for superusers
        if request.user.is_superuser:
            return None
        
        # Get the URL name
        try:
            url_name = resolve(request.path_info).url_name
            namespace = resolve(request.path_info).namespace
        except:
            return None
        
        # Skip exempt URLs
        if url_name in self.EXEMPT_URLS:
            return None
        
        # Skip if no namespace (usually means it's a root URL)
        if not namespace:
            return None
        
        # Check if this is an admin URL
        if namespace == 'admin':
            if request.user.role != 'admin' and not request.user.is_staff:
                messages.error(request, 'You do not have permission to access the admin interface.')
                return redirect('dashboard')
            return None
        
        # Get the app name from the namespace
        app_name = self.APP_NAMESPACE_MAP.get(namespace)
        if not app_name:
            return None  # Unknown namespace, let it through (will likely 404)
        
        # Check if user has access to this app
        if not has_app_access(request.user, app_name):
            return self._render_restricted(request, app_name, 'access')
        
        # Additional permission checks for specific actions
        if url_name and any(action in url_name for action in ['create', 'add', 'new']):
            if not has_permission(request.user, app_name, 'create'):
                return self._render_restricted(request, app_name, 'create')
        
        elif url_name and any(action in url_name for action in ['edit', 'update', 'change']):
            if not has_permission(request.user, app_name, 'update'):
                return self._render_restricted(request, app_name, 'update')
        
        elif url_name and any(action in url_name for action in ['delete', 'remove']):
            if not has_permission(request.user, app_name, 'delete'):
                return self._render_restricted(request, app_name, 'delete')
        
        return None
    
    def _render_restricted(self, request, app_name, action):
        """Render the access restricted page"""
        app_display = app_name.replace('_', ' ').title()
        context = {
            'restricted_app': app_display,
            'restricted_action': action,
            'user_role': request.user.get_role_display(),
        }
        response = render(request, 'accounts/access_restricted.html', context)
        response.status_code = 403
        return response


class DataAccessControlMiddleware:
    """
    Middleware to prevent users from accessing data they shouldn't see.
    This includes checking for direct object access via URLs.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the response is a 404 and user tried to access restricted data
        if response.status_code == 404 and request.user.is_authenticated:
            # Log potential unauthorized access attempt
            if hasattr(request, 'resolver_match') and request.resolver_match:
                namespace = request.resolver_match.namespace
                if namespace in RoleBasedAccessMiddleware.APP_NAMESPACE_MAP:
                    app_name = RoleBasedAccessMiddleware.APP_NAMESPACE_MAP[namespace]
                    if not has_app_access(request.user, app_name):
                        messages.warning(
                            request,
                            f'The requested resource does not exist or you do not have permission to access it.'
                        )
                        return redirect('dashboard')
        
        return response
