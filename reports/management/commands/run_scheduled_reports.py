from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reports.models import ScheduledReport, ReportAuditLog
from reports.utils import send_scheduled_report
from reports.views import (
    generate_dashboard_export_data,
    generate_patient_export_data,
    generate_financial_export_data,
    generate_appointment_export_data
)
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run scheduled reports and send them via email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually sending reports',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force run all active scheduled reports regardless of schedule',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force_run = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Starting scheduled reports processing...')
        )
        
        # Get scheduled reports that should run
        if force_run:
            scheduled_reports = ScheduledReport.objects.filter(status='active')
            self.stdout.write(f'Force running {scheduled_reports.count()} active scheduled reports')
        else:
            scheduled_reports = ScheduledReport.objects.filter(
                status='active',
                next_run__lte=timezone.now()
            )
            self.stdout.write(f'Found {scheduled_reports.count()} scheduled reports to run')
        
        success_count = 0
        error_count = 0
        
        for scheduled_report in scheduled_reports:
            try:
                self.stdout.write(f'Processing: {scheduled_report.configuration.name}')
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'DRY RUN: Would send report to {scheduled_report.recipients}')
                    )
                    continue
                
                # Generate report data based on configuration
                report_config = scheduled_report.configuration
                parameters = report_config.parameters or {}
                
                # Generate content data based on report type
                if report_config.report_type == 'dashboard':
                    content_data = generate_dashboard_export_data(parameters)
                elif report_config.report_type == 'patient':
                    content_data = generate_patient_export_data(parameters)
                elif report_config.report_type == 'financial':
                    content_data = generate_financial_export_data(parameters)
                elif report_config.report_type == 'appointment':
                    content_data = generate_appointment_export_data(parameters)
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Unknown report type: {report_config.report_type}')
                    )
                    continue
                
                # Send the report
                success = send_scheduled_report(scheduled_report, content_data)
                
                if success:
                    # Update scheduled report
                    scheduled_report.last_run = timezone.now()
                    scheduled_report.run_count += 1
                    scheduled_report.failure_count = 0  # Reset failure count on success
                    
                    # Calculate next run time based on frequency
                    if scheduled_report.configuration.schedule_frequency == 'daily':
                        scheduled_report.next_run = timezone.now() + timedelta(days=1)
                    elif scheduled_report.configuration.schedule_frequency == 'weekly':
                        scheduled_report.next_run = timezone.now() + timedelta(weeks=1)
                    elif scheduled_report.configuration.schedule_frequency == 'monthly':
                        scheduled_report.next_run = timezone.now() + timedelta(days=30)
                    elif scheduled_report.configuration.schedule_frequency == 'quarterly':
                        scheduled_report.next_run = timezone.now() + timedelta(days=90)
                    
                    scheduled_report.save()
                    
                    # Log successful run
                    ReportAuditLog.objects.create(
                        user=report_config.created_by,
                        report_type=report_config.report_type,
                        report_name=report_config.name,
                        action='scheduled',
                        parameters=parameters,
                        execution_time=0,  # Could be measured if needed
                        record_count=len(content_data.get('tables', [{}])[0].get('data', [])),
                        success=True
                    )
                    
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Successfully sent: {report_config.name}')
                    )
                    
                else:
                    # Handle failure
                    scheduled_report.failure_count += 1
                    
                    # Disable if too many failures
                    if scheduled_report.failure_count >= scheduled_report.max_failures:
                        scheduled_report.status = 'failed'
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Disabled report after {scheduled_report.max_failures} failures: {report_config.name}'
                            )
                        )
                    
                    scheduled_report.save()
                    
                    # Log failed run
                    ReportAuditLog.objects.create(
                        user=report_config.created_by,
                        report_type=report_config.report_type,
                        report_name=report_config.name,
                        action='scheduled',
                        parameters=parameters,
                        execution_time=0,
                        success=False,
                        error_message='Failed to send scheduled report email'
                    )
                    
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to send: {report_config.name}')
                    )
                    
            except Exception as e:
                error_count += 1
                logger.error(f'Error processing scheduled report {scheduled_report.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {scheduled_report.configuration.name}: {str(e)}')
                )
                
                # Update failure count
                scheduled_report.failure_count += 1
                if scheduled_report.failure_count >= scheduled_report.max_failures:
                    scheduled_report.status = 'failed'
                scheduled_report.save()
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Scheduled Reports Processing Complete')
        self.stdout.write(f'Successfully sent: {success_count}')
        self.stdout.write(f'Errors: {error_count}')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('This was a dry run - no reports were actually sent')
            )
        
        # Clean up old audit logs (optional)
        self.cleanup_old_logs()
    
    def cleanup_old_logs(self):
        """Clean up audit logs older than 90 days"""
        cutoff_date = timezone.now() - timedelta(days=90)
        old_logs = ReportAuditLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        
        if count > 0:
            old_logs.delete()
            self.stdout.write(f'Cleaned up {count} old audit log entries')
