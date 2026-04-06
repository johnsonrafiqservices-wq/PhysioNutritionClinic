"""
Template tags for permission checking in templates
Usage: {% load permission_tags %}
"""

from django import template
from accounts.permissions import has_app_access, has_permission, get_user_permissions

register = template.Library()


@register.filter
def has_app(user, app_name):
    """
    Check if user has access to app
    Usage: {% if user|has_app:'patients' %}
    """
    return has_app_access(user, app_name)


@register.filter
def can(user, permission_string):
    """
    Check if user has permission
    Usage: {% if user|can:'patients:create' %}
    permission_string format: 'app_name:permission'
    """
    try:
        app_name, permission = permission_string.split(':')
        return has_permission(user, app_name, permission)
    except ValueError:
        return False


@register.simple_tag
def user_can(user, app_name, permission):
    """
    Check if user has specific permission for app
    Usage: {% user_can user 'patients' 'create' as can_create %}
    """
    return has_permission(user, app_name, permission)


@register.simple_tag
def user_permissions_for(user, app_name):
    """
    Get all permissions user has for an app
    Usage: {% user_permissions_for user 'patients' as perms %}
    """
    return get_user_permissions(user, app_name)


@register.inclusion_tag('permissions/permission_denied.html', takes_context=True)
def show_permission_denied(context, message=None):
    """
    Show permission denied message
    Usage: {% show_permission_denied 'You cannot access this feature' %}
    """
    return {
        'message': message or 'You do not have permission to access this feature.',
        'user': context.get('user'),
    }
