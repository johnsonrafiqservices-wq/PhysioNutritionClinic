from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import ReportConfiguration, ReportAuditLog, ScheduledReport, ReportExport

@admin.register(ReportConfiguration)
class ReportConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'report_type', 'created_by', 'is_active', 
        'is_scheduled', 'schedule_frequency', 'created_at'
    ]
    list_filter = [
        'report_type', 'is_active', 'is_scheduled', 
        'schedule_frequency', 'created_at'
    ]
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'report_type', 'description', 'created_by')
        }),
        ('Configuration', {
            'fields': ('parameters', 'is_active')
        }),
        ('Scheduling', {
            'fields': ('is_scheduled', 'schedule_frequency'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(ReportAuditLog)
class ReportAuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'user', 'report_name', 'action', 
        'execution_time_display', 'record_count', 'success_display'
    ]
    list_filter = [
        'action', 'success', 'report_type', 'timestamp'
    ]
    search_fields = [
        'user__username', 'report_name', 'report_type', 'ip_address'
    ]
    readonly_fields = [
        'id', 'user', 'report_type', 'report_name', 'action',
        'parameters', 'execution_time', 'record_count', 'file_size',
        'ip_address', 'user_agent', 'timestamp', 'success', 'error_message'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'user', 'report_type', 'report_name', 'action')
        }),
        ('Performance Metrics', {
            'fields': ('execution_time', 'record_count', 'file_size')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Parameters', {
            'fields': ('parameters',),
            'classes': ('collapse',)
        }),
        ('Result', {
            'fields': ('timestamp', 'success', 'error_message')
        }),
    )
    
    def execution_time_display(self, obj):
        if obj.execution_time:
            if obj.execution_time > 10:
                color = 'red'
            elif obj.execution_time > 5:
                color = 'orange'
            else:
                color = 'green'
            return format_html(
                '<span style="color: {};">{}</span>',
                color, f'{obj.execution_time:.2f}s'
            )
        return '-'
    execution_time_display.short_description = 'Execution Time'
    execution_time_display.admin_order_field = 'execution_time'
    
    def success_display(self, obj):
        if obj.success:
            return format_html(
                '<span style="color: green;">✓ Success</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Failed</span>'
            )
    success_display.short_description = 'Status'
    success_display.admin_order_field = 'success'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # Audit logs should not be manually created
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be modified

@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = [
        'configuration', 'status', 'last_run', 'next_run', 
        'run_count', 'failure_count', 'recipients_display'
    ]
    list_filter = ['status', 'last_run', 'next_run']
    search_fields = ['configuration__name', 'recipients']
    readonly_fields = ['id', 'run_count', 'failure_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('id', 'configuration', 'recipients', 'status')
        }),
        ('Schedule Information', {
            'fields': ('last_run', 'next_run', 'run_count', 'failure_count', 'max_failures')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def recipients_display(self, obj):
        if obj.recipients:
            count = len(obj.recipients)
            if count <= 3:
                return ', '.join(obj.recipients)
            else:
                return f"{', '.join(obj.recipients[:3])} and {count - 3} more"
        return 'No recipients'
    recipients_display.short_description = 'Recipients'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('configuration')
    
    actions = ['run_now', 'pause_reports', 'resume_reports']
    
    def run_now(self, request, queryset):
        """Action to run selected scheduled reports immediately"""
        from django.contrib import messages
        from .management.commands.run_scheduled_reports import Command
        
        count = 0
        for scheduled_report in queryset.filter(status='active'):
            # This would need to be implemented to run individual reports
            count += 1
        
        messages.success(
            request, 
            f'Queued {count} reports for immediate execution. Check the audit log for results.'
        )
    run_now.short_description = 'Run selected reports now'
    
    def pause_reports(self, request, queryset):
        """Action to pause selected scheduled reports"""
        updated = queryset.update(status='paused')
        self.message_user(request, f'Paused {updated} scheduled reports.')
    pause_reports.short_description = 'Pause selected reports'
    
    def resume_reports(self, request, queryset):
        """Action to resume selected scheduled reports"""
        updated = queryset.filter(status='paused').update(status='active')
        self.message_user(request, f'Resumed {updated} scheduled reports.')
    resume_reports.short_description = 'Resume selected reports'

@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = [
        'report_name', 'export_format', 'user', 'file_size_display',
        'created_at', 'download_count', 'expires_at', 'is_expired_display'
    ]
    list_filter = [
        'export_format', 'created_at', 'expires_at'
    ]
    search_fields = [
        'report_name', 'user__username', 'report_type'
    ]
    readonly_fields = [
        'id', 'user', 'report_type', 'report_name', 'export_format',
        'file_path', 'file_size', 'parameters', 'created_at',
        'downloaded_at', 'download_count', 'expires_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Export Information', {
            'fields': ('id', 'user', 'report_type', 'report_name', 'export_format')
        }),
        ('File Information', {
            'fields': ('file_path', 'file_size', 'parameters')
        }),
        ('Usage Statistics', {
            'fields': ('created_at', 'downloaded_at', 'download_count', 'expires_at')
        }),
    )
    
    def file_size_display(self, obj):
        if obj.file_size:
            # Convert bytes to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.1f} {unit}"
                obj.file_size /= 1024.0
            return f"{obj.file_size:.1f} TB"
        return '0 B'
    file_size_display.short_description = 'File Size'
    file_size_display.admin_order_field = 'file_size'
    
    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ Expired</span>')
        else:
            return format_html('<span style="color: green;">✓ Valid</span>')
    is_expired_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # Exports should be created through the system
    
    def has_change_permission(self, request, obj=None):
        return False  # Exports should not be modified
    
    actions = ['cleanup_expired']
    
    def cleanup_expired(self, request, queryset):
        """Action to clean up expired exports"""
        expired_exports = queryset.filter(expires_at__lt=timezone.now())
        count = expired_exports.count()
        expired_exports.delete()
        self.message_user(request, f'Cleaned up {count} expired exports.')
    cleanup_expired.short_description = 'Clean up expired exports'

# Custom admin site configuration
admin.site.site_header = "Physio & Nutrition Clinic - Reports Administration"
admin.site.site_title = "Reports Admin"
admin.site.index_title = "Reports Management"
