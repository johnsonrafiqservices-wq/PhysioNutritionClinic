from django.contrib import admin
from .models import ClinicSettings, EnabledModule


@admin.register(EnabledModule)
class EnabledModuleAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'module_name', 'is_enabled', 'icon', 'order']
    list_editable = ['is_enabled', 'order']
    list_filter = ['is_enabled']
    search_fields = ['display_name', 'module_name']
    ordering = ['order']
    
    fieldsets = (
        ('Module Information', {
            'fields': ('module_name', 'display_name', 'icon')
        }),
        ('Status', {
            'fields': ('is_enabled', 'order')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClinicSettings)
class ClinicSettingsAdmin(admin.ModelAdmin):
    list_display = ['clinic_name', 'phone', 'email', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('clinic_name', 'logo')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow adding if no settings exist
        return not ClinicSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
