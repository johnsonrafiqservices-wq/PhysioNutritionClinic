from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q


# Available system modules that can be enabled/disabled
SYSTEM_MODULES = [
    ('patients', 'Patients Management'),
    ('appointments', 'Appointments'),
    ('medical_records', 'Medical Records'),
    ('laboratory', 'Laboratory'),
    ('pharmacy', 'Pharmacy'),
    ('billing', 'Billing'),
    ('budget', 'Budget & Expenses'),
    ('staff_management', 'Staff Management'),
    ('reports', 'Reports'),
]


class EnabledModule(models.Model):
    """
    Model to store which system modules are enabled.
    Only enabled modules will be shown in navigation and accessible.
    """
    hospital = models.ForeignKey(
        'tenants.Hospital',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enabled_modules',
    )
    module_name = models.CharField(
        max_length=50,
        choices=SYSTEM_MODULES,
        help_text="System module identifier"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Display name for the module"
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text="Whether this module is enabled and visible in the system"
    )
    icon = models.CharField(
        max_length=50,
        default='bi bi-box',
        help_text="Bootstrap icon class for the module"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in navigation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Enabled Module"
        verbose_name_plural = "Enabled Modules"
        ordering = ['order', 'display_name']
        unique_together = ('hospital', 'module_name')

    def __str__(self):
        status = "✓" if self.is_enabled else "✗"
        return f"{status} {self.display_name}"

    @classmethod
    def is_module_enabled(cls, module_name):
        """Check if a specific module is enabled"""
        try:
            module = cls.objects.get(module_name=module_name, hospital__isnull=True)
            return module.is_enabled
        except cls.DoesNotExist:
            return True
        except cls.MultipleObjectsReturned:
            return cls.objects.filter(module_name=module_name, hospital__isnull=True, is_enabled=True).exists()

    @classmethod
    def get_enabled_modules(cls):
        """Get list of enabled module names"""
        return list(cls.objects.filter(is_enabled=True, hospital__isnull=True).values_list('module_name', flat=True))

    @classmethod
    def initialize_modules(cls):
        """Initialize all system modules with default values"""
        default_icons = {
            'patients': 'bi bi-people',
            'appointments': 'bi bi-calendar-check',
            'medical_records': 'bi bi-folder-fill',
            'laboratory': 'bi bi-flask',
            'pharmacy': 'bi bi-capsule',
            'billing': 'bi bi-credit-card',
            'budget': 'bi bi-wallet2',
            'staff_management': 'bi bi-person-badge',
            'reports': 'bi bi-graph-up',
        }
        
        for idx, (module_name, display_name) in enumerate(SYSTEM_MODULES):
            cls.objects.get_or_create(
                module_name=module_name,
                hospital=None,
                defaults={
                    'display_name': display_name,
                    'is_enabled': True,
                    'icon': default_icons.get(module_name, 'bi bi-box'),
                    'order': idx * 10,
                }
            )


class ClinicSettings(models.Model):
    """
    Singleton model to store clinic-wide settings like logo and name.
    Only one instance should exist.
    """
    clinic_name = models.CharField(
        max_length=200,
        default="Alafia Point Wellness Clinic",
        help_text="The name of your clinic"
    )
    logo = models.ImageField(
        upload_to='clinic_logos/',
        blank=True,
        null=True,
        help_text="Upload your clinic logo (recommended size: 200x80px)"
    )
    address = models.TextField(
        blank=True,
        help_text="Clinic address"
    )
    box_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="P.O. Box number (e.g., P.O.Box 200210, Kampala - Uganda)"
    )
    postal_address = models.TextField(
        blank=True,
        help_text="Postal address (street address for mail delivery)"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Clinic phone number"
    )
    email = models.EmailField(
        blank=True,
        help_text="Clinic email address"
    )
    website = models.URLField(
        blank=True,
        help_text="Clinic website URL"
    )
    
    # Theme Customization Fields
    # Color validator for hex colors
    color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Enter a valid hex color code (e.g., #1B5E96)'
    )
    
    # Primary Colors
    primary_color = models.CharField(
        max_length=7,
        default='#1B5E96',
        validators=[color_validator],
        help_text='Primary brand color (default: #1B5E96)'
    )
    primary_dark = models.CharField(
        max_length=7,
        default='#154a7a',
        validators=[color_validator],
        help_text='Dark variant of primary color'
    )
    primary_light = models.CharField(
        max_length=7,
        default='#e6f1fa',
        validators=[color_validator],
        help_text='Light variant of primary color'
    )
    
    # Success Colors
    success_color = models.CharField(
        max_length=7,
        default='#2E8B57',
        validators=[color_validator],
        help_text='Success/positive action color'
    )
    success_dark = models.CharField(
        max_length=7,
        default='#236b43',
        validators=[color_validator],
        help_text='Dark variant of success color'
    )
    success_light = models.CharField(
        max_length=7,
        default='#e8f5f0',
        validators=[color_validator],
        help_text='Light variant of success color'
    )
    
    # Accent Colors
    accent_color = models.CharField(
        max_length=7,
        default='#00A86B',
        validators=[color_validator],
        help_text='Accent/highlight color'
    )
    accent_dark = models.CharField(
        max_length=7,
        default='#008554',
        validators=[color_validator],
        help_text='Dark variant of accent color'
    )
    accent_light = models.CharField(
        max_length=7,
        default='#e6f9f3',
        validators=[color_validator],
        help_text='Light variant of accent color'
    )
    
    # Warning Colors
    warning_color = models.CharField(
        max_length=7,
        default='#FF8C00',
        validators=[color_validator],
        help_text='Warning/caution color'
    )
    warning_dark = models.CharField(
        max_length=7,
        default='#e67e00',
        validators=[color_validator],
        help_text='Dark variant of warning color'
    )
    warning_light = models.CharField(
        max_length=7,
        default='#fff4e6',
        validators=[color_validator],
        help_text='Light variant of warning color'
    )
    
    # Danger Colors
    danger_color = models.CharField(
        max_length=7,
        default='#dc2626',
        validators=[color_validator],
        help_text='Danger/error color'
    )
    danger_dark = models.CharField(
        max_length=7,
        default='#b91c1c',
        validators=[color_validator],
        help_text='Dark variant of danger color'
    )
    danger_light = models.CharField(
        max_length=7,
        default='#fecaca',
        validators=[color_validator],
        help_text='Light variant of danger color'
    )
    
    # Info Colors
    info_color = models.CharField(
        max_length=7,
        default='#0891b2',
        validators=[color_validator],
        help_text='Info/informational color'
    )
    info_dark = models.CharField(
        max_length=7,
        default='#0e7490',
        validators=[color_validator],
        help_text='Dark variant of info color'
    )
    info_light = models.CharField(
        max_length=7,
        default='#cffafe',
        validators=[color_validator],
        help_text='Light variant of info color'
    )
    
    # Secondary/Neutral Colors
    secondary_color = models.CharField(
        max_length=7,
        default='#64748b',
        validators=[color_validator],
        help_text='Secondary/neutral color'
    )
    secondary_dark = models.CharField(
        max_length=7,
        default='#475569',
        validators=[color_validator],
        help_text='Dark variant of secondary color'
    )
    secondary_light = models.CharField(
        max_length=7,
        default='#f1f5f9',
        validators=[color_validator],
        help_text='Light variant of secondary color'
    )
    
    # Base Colors
    dark_color = models.CharField(
        max_length=7,
        default='#1e293b',
        validators=[color_validator],
        help_text='Dark text/background color'
    )
    light_color = models.CharField(
        max_length=7,
        default='#f8fafc',
        validators=[color_validator],
        help_text='Light background color'
    )
    border_color = models.CharField(
        max_length=7,
        default='#e2e8f0',
        validators=[color_validator],
        help_text='Border color'
    )
    
    # Text Colors
    text_primary = models.CharField(
        max_length=7,
        default='#1e293b',
        validators=[color_validator],
        help_text='Primary text color'
    )
    text_secondary = models.CharField(
        max_length=7,
        default='#64748b',
        validators=[color_validator],
        help_text='Secondary text color'
    )
    text_muted = models.CharField(
        max_length=7,
        default='#94a3b8',
        validators=[color_validator],
        help_text='Muted text color'
    )
    
    # Background Colors
    bg_primary = models.CharField(
        max_length=7,
        default='#ffffff',
        validators=[color_validator],
        help_text='Primary background color'
    )
    bg_secondary = models.CharField(
        max_length=7,
        default='#f8fafc',
        validators=[color_validator],
        help_text='Secondary background color'
    )
    bg_tertiary = models.CharField(
        max_length=7,
        default='#f1f5f9',
        validators=[color_validator],
        help_text='Tertiary background color'
    )
    
    # Chart Colors (for graphs and visualizations)
    chart_color_1 = models.CharField(
        max_length=7,
        default='#1B5E96',
        validators=[color_validator],
        help_text='Chart color 1'
    )
    chart_color_2 = models.CharField(
        max_length=7,
        default='#2E8B57',
        validators=[color_validator],
        help_text='Chart color 2'
    )
    chart_color_3 = models.CharField(
        max_length=7,
        default='#00A86B',
        validators=[color_validator],
        help_text='Chart color 3'
    )
    chart_color_4 = models.CharField(
        max_length=7,
        default='#FF8C00',
        validators=[color_validator],
        help_text='Chart color 4'
    )
    chart_color_5 = models.CharField(
        max_length=7,
        default='#0891b2',
        validators=[color_validator],
        help_text='Chart color 5'
    )
    chart_color_6 = models.CharField(
        max_length=7,
        default='#dc2626',
        validators=[color_validator],
        help_text='Chart color 6'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clinic Settings"
        verbose_name_plural = "Clinic Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and ClinicSettings.objects.exists():
            raise ValidationError('Only one ClinicSettings instance is allowed.')
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create the clinic settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def __str__(self):
        return f"Settings for {self.clinic_name}"
