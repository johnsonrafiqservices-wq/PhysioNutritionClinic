from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class ReportConfiguration(models.Model):
    """Model to store custom report configurations"""
    REPORT_TYPES = [
        ('patient', 'Patient Reports'),
        ('financial', 'Financial Reports'),
        ('appointment', 'Appointment Reports'),
        ('custom', 'Custom Reports'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict, help_text="Report parameters and filters")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ])
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class ReportAuditLog(models.Model):
    """Model to track report generation and access for audit purposes"""
    ACTION_TYPES = [
        ('generated', 'Report Generated'),
        ('viewed', 'Report Viewed'),
        ('exported_pdf', 'Exported to PDF'),
        ('exported_excel', 'Exported to Excel'),
        ('emailed', 'Report Emailed'),
        ('scheduled', 'Scheduled Report Run'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_activities')
    report_type = models.CharField(max_length=50)
    report_name = models.CharField(max_length=200)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    parameters = models.JSONField(default=dict, help_text="Parameters used for report generation")
    execution_time = models.FloatField(help_text="Time taken to generate report in seconds")
    record_count = models.IntegerField(default=0, help_text="Number of records in the report")
    file_size = models.IntegerField(default=0, help_text="File size in bytes for exports")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['report_type', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.report_name} - {self.get_action_display()}"

class ScheduledReport(models.Model):
    """Model for managing scheduled report deliveries"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    configuration = models.ForeignKey(ReportConfiguration, on_delete=models.CASCADE, related_name='schedules')
    recipients = models.JSONField(default=list, help_text="List of email addresses to send reports to")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()
    run_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    max_failures = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['next_run']
        
    def __str__(self):
        return f"Scheduled: {self.configuration.name}"
        
    def should_run(self):
        """Check if the scheduled report should run now"""
        return self.status == 'active' and self.next_run <= timezone.now()

class ReportExport(models.Model):
    """Model to track report exports and downloads"""
    EXPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_exports')
    report_type = models.CharField(max_length=50)
    report_name = models.CharField(max_length=200)
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.IntegerField(default=0)
    parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    download_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(help_text="When the export file expires")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.report_name} - {self.export_format.upper()}"
        
    def is_expired(self):
        """Check if the export has expired"""
        return timezone.now() > self.expires_at
