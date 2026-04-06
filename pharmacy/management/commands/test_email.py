"""
Management command to test email configuration
Usage: python manage.py test_email recipient@email.com
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            nargs='?',
            type=str,
            default=None,
            help='Email address to send test email to'
        )

    def handle(self, *args, **options):
        recipient = options.get('recipient')
        
        if not recipient:
            self.stdout.write(self.style.ERROR('Please provide a recipient email address.'))
            self.stdout.write('Usage: python manage.py test_email recipient@email.com')
            return
        
        # Display current configuration
        self.stdout.write(self.style.WARNING('\n=== Current Email Configuration ==='))
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'EMAIL_HOST_PASSWORD: {"*" * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else "NOT SET"}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'EMAIL_TIMEOUT: {settings.EMAIL_TIMEOUT}')
        
        # Check for console backend
        if 'console' in settings.EMAIL_BACKEND.lower():
            self.stdout.write(self.style.SUCCESS('\n✓ Using console backend - emails will print to console'))
        
        self.stdout.write(self.style.WARNING(f'\n=== Sending Test Email to {recipient} ==='))
        
        # Try sending simple email
        try:
            send_mail(
                subject='Test Email from PhysioNutrition Clinic',
                message='This is a test email to verify email configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('\n✓ Simple test email sent successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Simple email failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('\nCommon issues:'))
            self.stdout.write('  1. Incorrect EMAIL_HOST_PASSWORD (use Gmail App Password)')
            self.stdout.write('  2. Gmail requires App Password: https://myaccount.google.com/apppasswords')
            self.stdout.write('  3. Network/firewall blocking SMTP connection')
            self.stdout.write('  4. EMAIL_USE_TLS/EMAIL_USE_SSL misconfiguration')
            return
        
        # Try sending HTML email
        self.stdout.write(self.style.WARNING('\n=== Sending HTML Test Email ==='))
        try:
            from django.core.mail import EmailMultiAlternatives
            
            html_content = """
            <html>
                <body>
                    <h2>PhysioNutrition Clinic</h2>
                    <p>This is a <strong>test email</strong> with HTML content.</p>
                    <p>If you can see this formatted text, HTML emails are working correctly.</p>
                    <hr>
                    <p><small>Sent from PhysioNutrition Clinic Email Test</small></p>
                </body>
            </html>
            """
            
            email = EmailMultiAlternatives(
                subject='HTML Test Email from PhysioNutrition Clinic',
                body='This is the plain text version.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            self.stdout.write(self.style.SUCCESS('✓ HTML test email sent successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ HTML email failed: {str(e)}'))
            return
        
        # Final success message
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('✓ All email tests passed!'))
        self.stdout.write(self.style.SUCCESS('Email configuration is working correctly.'))
        self.stdout.write(self.style.SUCCESS('=' * 50 + '\n'))
        
        # Tips
        self.stdout.write(self.style.WARNING('Tips for production:'))
        self.stdout.write('  • Check spam folder if emails don\'t arrive')
        self.stdout.write('  • Gmail has daily sending limits (500 emails/day)')
        self.stdout.write('  • Consider using SendGrid or Amazon SES for production')
        self.stdout.write('  • Set up SPF/DKIM records for better deliverability')
