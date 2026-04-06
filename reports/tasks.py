"""
Scheduled report tasks for automated report generation and delivery
"""
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import ScheduledReport, ReportAuditLog
from .utils import ReportPDFGenerator
import logging

logger = logging.getLogger(__name__)

def send_scheduled_report(scheduled_report):
    """
    Generate and send a scheduled report via email
    """
    try:
        configuration = scheduled_report.configuration
        
        # Generate report data based on configuration type
        if configuration.report_type == 'patient':
            from .views import generate_patient_export_data
            report_data = generate_patient_export_data(configuration.parameters)
        elif configuration.report_type == 'financial':
            from .views import generate_financial_export_data
            report_data = generate_financial_export_data(configuration.parameters)
        elif configuration.report_type == 'appointment':
            from .views import generate_appointment_export_data
            report_data = generate_appointment_export_data(configuration.parameters)
        else:
            logger.error(f"Unknown report type: {configuration.report_type}")
            return False
        
        # Generate PDF
        pdf_generator = ReportPDFGenerator()
        pdf_buffer = pdf_generator.generate_report_pdf(
            title=configuration.name,
            data=report_data,
            report_type=configuration.report_type
        )
        
        # Prepare email
        subject = f"Scheduled Report: {configuration.name}"
        html_message = render_to_string('reports/email/scheduled_report.html', {
            'report_name': configuration.name,
            'report_type': configuration.get_report_type_display(),
            'generated_at': timezone.now(),
            'frequency': scheduled_report.configuration.get_schedule_frequency_display() if scheduled_report.configuration.schedule_frequency else 'One-time',
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@physionutritionclinic.com',
            to=scheduled_report.recipients,
        )
        email.content_subtype = 'html'
        
        # Attach PDF
        email.attach(
            f"{configuration.name}_{timezone.now().strftime('%Y%m%d')}.pdf",
            pdf_buffer.getvalue(),
            'application/pdf'
        )
        
        # Send email
        email.send()
        
        # Update scheduled report
        scheduled_report.last_run = timezone.now()
        scheduled_report.run_count += 1
        scheduled_report.failure_count = 0
        
        # Calculate next run based on frequency
        if configuration.schedule_frequency == 'daily':
            scheduled_report.next_run = timezone.now() + timedelta(days=1)
        elif configuration.schedule_frequency == 'weekly':
            scheduled_report.next_run = timezone.now() + timedelta(weeks=1)
        elif configuration.schedule_frequency == 'monthly':
            scheduled_report.next_run = timezone.now() + timedelta(days=30)
        elif configuration.schedule_frequency == 'quarterly':
            scheduled_report.next_run = timezone.now() + timedelta(days=90)
        
        scheduled_report.save()
        
        # Log activity
        ReportAuditLog.objects.create(
            user=configuration.created_by,
            report_type=configuration.report_type,
            report_name=configuration.name,
            action='scheduled',
            parameters=configuration.parameters,
            execution_time=0,
            record_count=0,
            success=True
        )
        
        logger.info(f"Successfully sent scheduled report: {configuration.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending scheduled report: {str(e)}")
        
        # Update failure count
        scheduled_report.failure_count += 1
        if scheduled_report.failure_count >= scheduled_report.max_failures:
            scheduled_report.status = 'failed'
        scheduled_report.save()
        
        # Log failure
        ReportAuditLog.objects.create(
            user=configuration.created_by,
            report_type=configuration.report_type,
            report_name=configuration.name,
            action='scheduled',
            parameters=configuration.parameters,
            execution_time=0,
            record_count=0,
            success=False,
            error_message=str(e)
        )
        
        return False

def run_scheduled_reports():
    """
    Run all scheduled reports that are due
    """
    scheduled_reports = ScheduledReport.objects.filter(
        status='active',
        next_run__lte=timezone.now()
    )
    
    results = {
        'total': scheduled_reports.count(),
        'success': 0,
        'failed': 0
    }
    
    for scheduled_report in scheduled_reports:
        if send_scheduled_report(scheduled_report):
            results['success'] += 1
        else:
            results['failed'] += 1
    
    logger.info(f"Scheduled reports run complete: {results}")
    return results
