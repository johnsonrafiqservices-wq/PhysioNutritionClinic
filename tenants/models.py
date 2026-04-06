from django.db import models


class Hospital(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    SUBSCRIPTION_PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    subdomain = models.CharField(
        max_length=100, unique=True, blank=True,
        help_text="Subdomain prefix (e.g. 'hospital1' for hospital1.yourdomain.com)"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Uganda')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription_expires = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='hospital_logos/', null=True, blank=True)
    contact_person = models.CharField(
        max_length=150, blank=True,
        help_text='Primary contact person name'
    )
    max_patients = models.PositiveIntegerField(
        default=500, help_text='Maximum number of patients allowed'
    )
    max_users = models.PositiveIntegerField(
        default=10, help_text='Maximum number of staff users allowed'
    )
    notes = models.TextField(blank=True, help_text='Internal admin notes about this hospital')
    subscription_plan = models.CharField(
        max_length=20, choices=SUBSCRIPTION_PLAN_CHOICES,
        blank=True, default='free'
    )

    class Meta:
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']

    def __str__(self):
        return self.name
