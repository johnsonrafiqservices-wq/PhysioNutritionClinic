from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientGroup
from appointments.models import Appointment, Service
from decimal import Decimal

User = get_user_model()


class ServicePriceGroup(models.Model):
    """Per-group pricing override for services. Falls back to Service.base_price if no entry exists."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='group_prices')
    patient_group = models.ForeignKey(PatientGroup, on_delete=models.CASCADE, related_name='service_prices')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this service for this patient group")

    class Meta:
        unique_together = ('service', 'patient_group')
        ordering = ['service', 'patient_group']
        verbose_name = 'Service Group Price'
        verbose_name_plural = 'Service Group Prices'

    def __str__(self):
        return f"{self.service.name} – {self.patient_group.name}: {self.price}"

    @staticmethod
    def get_price_for_patient(service, patient):
        """Return group-specific price if available, otherwise the service default."""
        if patient and patient.patient_group_id:
            try:
                entry = ServicePriceGroup.objects.get(service=service, patient_group=patient.patient_group)
                return entry.price
            except ServicePriceGroup.DoesNotExist:
                pass
        return service.base_price

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice details
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional info
    notes = models.TextField(blank=True)
    invoice_pdf_url = models.URLField(blank=True, help_text="Cloudinary URL for published invoice PDF")
    gdrive_pdf_url = models.URLField(blank=True, help_text="Google Drive URL for published invoice PDF")
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_totals(self):
        """Calculate invoice totals based on line items"""
        line_items = self.line_items.all()
        self.subtotal = sum(item.total_amount for item in line_items)
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()
    
    def get_total_paid(self):
        """Calculate total amount paid for this invoice"""
        return sum(payment.amount for payment in self.payments.filter(status='completed'))
    
    def get_balance_due(self):
        """Calculate remaining balance due"""
        return self.total_amount - self.get_total_paid()
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']

class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Lab test support
    lab_test_request = models.ForeignKey('laboratory.LabTestRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Recalculate invoice totals
        self.invoice.calculate_totals()
    
    def __str__(self):
        return f"{self.description} - {self.total_amount}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_id = models.CharField(max_length=20, unique=True)
    # Invoice is optional to allow general payments recorded against a patient only
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Payment details
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    receipt_pdf_url = models.URLField(blank=True, help_text="Cloudinary URL for published receipt PDF")
    gdrive_pdf_url = models.URLField(blank=True, help_text="Google Drive URL for published receipt PDF")
    
    # System fields
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - UGX {self.amount}"
    
    class Meta:
        ordering = ['-payment_date']

class InsuranceClaim(models.Model):
    CLAIM_STATUS = [
        ('submitted', 'Submitted'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('paid', 'Paid'),
    ]
    
    claim_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='insurance_claims')
    
    # Insurance details
    insurance_provider = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=50)
    group_number = models.CharField(max_length=50, blank=True)
    
    # Claim details
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='submitted')
    
    submission_date = models.DateField(auto_now_add=True)
    response_date = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True)
    
    # System fields
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Claim {self.claim_number} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-submission_date']

class BillingAuditLog(models.Model):
    ACTION_TYPES = [
        ('invoice_created', 'Invoice Created'),
        ('invoice_updated', 'Invoice Updated'),
        ('invoice_status_changed', 'Invoice Status Changed'),
        ('invoice_emailed', 'Invoice Emailed'),
        ('payment_created', 'Payment Created'),
        ('payment_refunded', 'Payment Refunded'),
        ('payment_status_changed', 'Payment Status Changed'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    details = models.TextField(blank=True)

    def __str__(self):
        user = self.performed_by.get_full_name() if self.performed_by else 'System'
        return f"{self.get_action_display()} by {user} at {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Billing Audit Log'
        verbose_name_plural = 'Billing Audit Logs'


class PaymentPlan(models.Model):
    PLAN_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    
    plan_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payment_plans')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payment_plans')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_payments = models.IntegerField()
    payments_made = models.IntegerField(default=0)
    
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=PLAN_STATUS, default='active')
    
    notes = models.TextField(blank=True)
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def remaining_balance(self):
        paid_amount = self.payments_made * self.monthly_payment
        return self.total_amount - paid_amount
    
    def __str__(self):
        return f"Payment Plan {self.plan_id} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']


class GroupInvoice(models.Model):
    """Invoice for a patient group covering services rendered over a time period"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    INVOICE_TYPE_CHOICES = [
        ('auto', 'Auto-Generated (Period)'),
        ('custom', 'Custom Invoice'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True)
    patient_group = models.ForeignKey(PatientGroup, on_delete=models.CASCADE, related_name='group_invoices')
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE_CHOICES, default='auto')
    
    # Period for auto-generated invoices
    period_start = models.DateField(null=True, blank=True, help_text="Start date for services included")
    period_end = models.DateField(null=True, blank=True, help_text="End date for services included")
    
    # Invoice details
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Billing contact
    billing_contact_name = models.CharField(max_length=200, blank=True)
    billing_contact_email = models.EmailField(blank=True)
    billing_contact_phone = models.CharField(max_length=20, blank=True)
    billing_address = models.TextField(blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Additional info
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    invoice_pdf_url = models.URLField(blank=True)
    gdrive_pdf_url = models.URLField(blank=True)
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Group Invoice'
        verbose_name_plural = 'Group Invoices'
    
    def __str__(self):
        return f"Group Invoice {self.invoice_number} - {self.patient_group.name}"
    
    def calculate_totals(self):
        """Calculate invoice totals based on line items"""
        items = self.items.all()
        self.subtotal = sum(item.total_amount for item in items)
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()
    
    def get_total_paid(self):
        """Calculate total amount paid for this invoice"""
        return sum(payment.amount for payment in self.group_payments.filter(status='completed'))
    
    def get_balance_due(self):
        """Calculate remaining balance due"""
        return self.total_amount - self.get_total_paid()
    
    def get_patient_count(self):
        """Get count of unique patients in this invoice"""
        return self.items.values('patient').distinct().count()
    
    def get_service_count(self):
        """Get total count of services/items"""
        return self.items.count()


class GroupInvoiceItem(models.Model):
    """Individual line items for group invoices"""
    group_invoice = models.ForeignKey(GroupInvoice, on_delete=models.CASCADE, related_name='items')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='group_invoice_items', null=True, blank=True)
    
    # Service references
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    lab_test_request = models.ForeignKey('laboratory.LabTestRequest', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Item details
    service_date = models.DateField()
    description = models.CharField(max_length=300)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional info
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['service_date', 'id']
        verbose_name = 'Group Invoice Item'
        verbose_name_plural = 'Group Invoice Items'
    
    def __str__(self):
        if self.patient:
            return f"{self.patient.get_full_name()} - {self.description}"
        return self.description
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Recalculate group invoice totals
        self.group_invoice.calculate_totals()


class GroupPayment(models.Model):
    """Payments made against group invoices"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('wire_transfer', 'Wire Transfer'),
        ('credit_card', 'Credit Card'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_id = models.CharField(max_length=20, unique=True)
    group_invoice = models.ForeignKey(GroupInvoice, on_delete=models.CASCADE, related_name='group_payments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Payment details
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    receipt_pdf_url = models.URLField(blank=True)
    gdrive_pdf_url = models.URLField(blank=True)
    
    # System fields
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Group Payment'
        verbose_name_plural = 'Group Payments'
    
    def __str__(self):
        return f"Payment {self.payment_id} - UGX {self.amount}"
