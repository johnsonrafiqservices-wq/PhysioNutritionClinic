"""
Enhanced Admin Configuration for Django Jet Reboot
This file contains configurations to enhance the admin interface
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

# Custom Admin Site Configuration
class ClinicAdminSite(AdminSite):
    """
    Custom admin site for the clinic system
    """
    site_header = _('PhysioNutrition Clinic Administration')
    site_title = _('Clinic Admin')
    index_title = _('Welcome to PhysioNutrition Clinic Administration')
    site_url = '/patients/'  # Link to main application
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        
        # Define custom ordering for apps
        app_order = [
            'patients',
            'appointments', 
            'billing',
            'medical_records',
            'laboratory',
            'inventory',
            'accounts',
            'clinic_settings',
            'reports',
        ]
        
        # Sort apps according to our custom order
        app_list = []
        for app_name in app_order:
            if app_name in app_dict:
                app_list.append(app_dict[app_name])
        
        # Add any remaining apps not in our custom order
        for app_name, app_data in app_dict.items():
            if app_name not in app_order:
                app_list.append(app_data)
        
        return app_list

# Enhanced Admin Mixins
class EnhancedAdminMixin:
    """
    Mixin to enhance admin interfaces with better defaults
    """
    list_per_page = 25
    show_full_result_count = False
    preserve_filters = True
    
    def get_list_display(self, request):
        """
        Enhanced list display with better defaults
        """
        list_display = super().get_list_display(request)
        if hasattr(self.model, 'created_at') and 'created_at' not in list_display:
            list_display = list_display + ('created_at',)
        if hasattr(self.model, 'updated_at') and 'updated_at' not in list_display:
            list_display = list_display + ('updated_at',)
        return list_display
    
    def get_list_filter(self, request):
        """
        Enhanced list filter with better defaults
        """
        list_filter = super().get_list_filter(request)
        if hasattr(self.model, 'created_at') and 'created_at' not in list_filter:
            list_filter = list_filter + ('created_at',)
        if hasattr(self.model, 'is_active') and 'is_active' not in list_filter:
            list_filter = list_filter + ('is_active',)
        return list_filter

class ReadOnlyAdminMixin:
    """
    Mixin for read-only admin interfaces
    """
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Custom Admin Actions
def mark_as_active(modeladmin, request, queryset):
    """
    Mark selected items as active
    """
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f'{updated} items marked as active.')
mark_as_active.short_description = _('Mark selected items as active')

def mark_as_inactive(modeladmin, request, queryset):
    """
    Mark selected items as inactive
    """
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} items marked as inactive.')
mark_as_inactive.short_description = _('Mark selected items as inactive')

# Export Actions
def export_as_csv(modeladmin, request, queryset):
    """
    Export selected items as CSV
    """
    import csv
    from django.http import HttpResponse
    
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)
    
    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])
    
    return response
export_as_csv.short_description = _('Export selected items as CSV')

# Common Admin Configuration
COMMON_ADMIN_ACTIONS = [mark_as_active, mark_as_inactive, export_as_csv]

# Admin Interface Customizations
def customize_admin_interface():
    """
    Apply customizations to the admin interface
    """
    # Customize admin site
    admin.site.site_header = _('PhysioNutrition Clinic Administration')
    admin.site.site_title = _('Clinic Admin')
    admin.site.index_title = _('Welcome to PhysioNutrition Clinic Administration')
    admin.site.site_url = '/patients/'
    
    # Add custom CSS and JS
    admin.site.enable_nav_sidebar = False  # Disable Django 3.1+ sidebar for Jet compatibility
