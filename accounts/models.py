from django.contrib.auth.models import AbstractUser
from django.db import models


SYSTEM_APPS = [
    ('patients', 'Patients'),
    ('appointments', 'Appointments'),
    ('billing', 'Billing & Finance'),
    ('medical_records', 'Medical Records'),
    ('laboratory', 'Laboratory'),
    ('pharmacy', 'Pharmacy'),
    ('reports', 'Reports & Analytics'),
    ('staff_management', 'Staff Management'),
    ('budget', 'Budget & Planning'),
    ('clinic_settings', 'Clinic Settings'),
]


class User(AbstractUser):
    ROLE_CHOICES = [
        # Administration & Management
        ('admin', 'System Administrator'),
        ('clinic_manager', 'Clinic Manager'),
        ('medical_director', 'Medical Director'),
        
        # Clinical Staff (Patients & Appointments)
        ('doctor', 'Doctor/General Practitioner'),
        ('physiotherapist', 'Physiotherapist'),
        ('nutritionist', 'Nutritionist/Dietitian'),
        ('nurse', 'Nurse'),
        ('clinical_assistant', 'Clinical Assistant'),
        
        # Reception & Front Desk (Appointments & Patient Registration)
        ('receptionist', 'Receptionist'),
        ('front_desk', 'Front Desk Officer'),
        ('appointment_coordinator', 'Appointment Coordinator'),
        
        # Laboratory (Laboratory App)
        ('lab_technician', 'Laboratory Technician'),
        ('lab_manager', 'Laboratory Manager'),
        ('pathologist', 'Pathologist'),
        
        # Pharmacy (Pharmacy App)
        ('pharmacist', 'Pharmacist'),
        ('pharmacy_assistant', 'Pharmacy Assistant'),
        ('pharmacy_manager', 'Pharmacy Manager'),
        
        # Billing & Finance (Billing App)
        ('billing_officer', 'Billing Officer'),
        ('accountant', 'Accountant'),
        ('finance_manager', 'Finance Manager'),
        ('cashier', 'Cashier'),
        
        # Medical Records (Medical Records App)
        ('medical_records_officer', 'Medical Records Officer'),
        ('records_manager', 'Records Manager'),
        ('data_entry_clerk', 'Data Entry Clerk'),
        
        # Reports & Analytics (Reports App)
        ('reports_analyst', 'Reports Analyst'),
        ('statistician', 'Statistician'),
        
        # Staff Management (Staff Management App)
        ('hr_manager', 'HR Manager'),
        ('hr_officer', 'HR Officer'),
        
        # Budget & Financial Planning (Budget App)
        ('budget_officer', 'Budget Officer'),
        ('financial_controller', 'Financial Controller'),
        
        # Support & Maintenance
        ('it_support', 'IT Support'),
        ('maintenance_staff', 'Maintenance Staff'),
    ]
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True)
    is_active_employee = models.BooleanField(default=True)
    date_joined_clinic = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    class Meta:
        db_table = 'accounts_user'


class UserAppPermission(models.Model):
    """Per-user app access overrides. Admins can grant or revoke access to specific apps."""
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='app_permissions'
    )
    app_name = models.CharField(max_length=50, choices=SYSTEM_APPS)
    is_allowed = models.BooleanField(
        default=True,
        help_text='If checked, user CAN access this app. If unchecked, user is BLOCKED.'
    )
    granted_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='permissions_granted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'app_name')
        ordering = ['user', 'app_name']
        verbose_name = 'User App Permission'
        verbose_name_plural = 'User App Permissions'

    def __str__(self):
        status = 'Allowed' if self.is_allowed else 'Blocked'
        return f"{self.user.get_full_name()} — {self.get_app_name_display()} ({status})"
