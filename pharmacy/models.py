from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Medication(models.Model):
    FORM_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('liquid', 'Liquid'),
        ('injection', 'Injection'),
        ('ointment', 'Ointment'),
        ('inhaler', 'Inhaler'),
        ('cream', 'Cream'),
        ('drops', 'Drops'),
        ('powder', 'Powder'),
        ('spray', 'Spray'),
    ]
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    strength = models.CharField(max_length=100)
    form = models.CharField(max_length=20, choices=FORM_CHOICES)
    reorder_level = models.PositiveIntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measure = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=200)
    storage_instructions = models.TextField(blank=True)
    requires_prescription = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.strength} ({self.form})"

    @property
    def current_stock(self):
        """Get current total stock across all active batches."""
        return self.batches.filter(
            is_active=True,
            expiry_date__gt=timezone.now()
        ).aggregate(
            total=models.Sum('quantity_remaining')
        )['total'] or 0

    @property
    def low_stock(self):
        """Check if current stock is at or below reorder level."""
        return self.current_stock <= self.reorder_level


class MedicationUnit(models.Model):
    """Different units of measurement and their prices for a medication.
    Example: A medication sold as Box (base unit) can also be sold as:
    - Strip (10 strips per box)
    - Tablet (100 tablets per box)
    """
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='units')
    unit_name = models.CharField(max_length=50, help_text="e.g., Tablet, Strip, Bottle, Sachet")
    quantity_per_base = models.PositiveIntegerField(
        default=1, 
        help_text="How many of this unit are in the base unit (e.g., 10 strips per box)"
    )
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this unit")
    is_default = models.BooleanField(default=False, help_text="Is this the default selling unit?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'unit_name']
        unique_together = ['medication', 'unit_name']

    def __str__(self):
        return f"{self.medication.name} - {self.unit_name} @ {self.selling_price}"

    def save(self, *args, **kwargs):
        # Ensure only one default unit per medication
        if self.is_default:
            MedicationUnit.objects.filter(
                medication=self.medication, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment')
    ]
    
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=200, blank=True)  # e.g., prescription ID, adjustment reason
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type} - {self.quantity} units ({self.reference})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantity <= 0:
            raise ValidationError('Quantity must be positive')
        
        if self.movement_type in ['out', 'adjustment']:
            if self.quantity > self.batch.quantity_remaining:
                raise ValidationError(
                    f'Insufficient stock. Available: {self.batch.quantity_remaining}, '
                    f'Requested: {self.quantity}'
                )
    
    def save(self, *args, **kwargs):
        """Save movement as an audit record only, without changing batch stock.

        Stock level changes are handled explicitly in views/business logic.
        """
        self.clean()
        super().save(*args, **kwargs)


class Batch(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('quarantine', 'Quarantine'),
        ('expired', 'Expired')
    ]
    
    medication = models.ForeignKey(Medication, related_name='batches', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    batch_number = models.CharField(max_length=100, unique=True)
    # branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, null=True, blank=True)  # Disabled - branches app not available
    quantity_remaining = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    received_date = models.DateField(auto_now_add=True)
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='received_batches', null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    last_quality_check = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Batches"

    def __str__(self):
        return f"{self.medication.name} - Batch {self.batch_number}"

    @property
    def is_expired(self):
        return self.expiry_date <= timezone.now().date()

    @property
    def is_expiring_soon(self):
        """Check if batch expires within 90 days."""
        if self.is_expired:
            return False
        return (self.expiry_date - timezone.now().date()).days <= 90

    def get_remaining_shelf_life_days(self):
        return (self.expiry_date - timezone.now().date()).days
    
    @property
    def days_until_expiry(self):
        """Get the number of days until the batch expires"""
        return (self.expiry_date - timezone.now().date()).days

class StockAlert(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('resolved', 'Resolved')
    ]
    
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='stock_alerts')
    current_stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stock Alert - {self.medication.name} (Current: {self.current_stock})"
        
    class Meta:
        ordering = ['-created_at']



class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # visit = models.ForeignKey('ehr.Visit', on_delete=models.CASCADE, null=True, blank=True)  # Disabled - ehr app not available
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, null=True, blank=True)  # Using patients app instead
    
    # Legacy fields for backward compatibility (keep for existing prescriptions)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, null=True, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    
    instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    prescribed_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
    prescribed_date = models.DateTimeField(auto_now_add=True)
    dispensed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   limit_choices_to={'role': 'pharmacist'}, related_name='dispensed_prescriptions')
    dispensed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        patient_name = self.patient.get_full_name() if self.patient else "Unknown Patient"
        if self.medication:  # Legacy single medication
            return f"Prescription for {patient_name} - {self.medication.name}"
        else:  # New multi-medication
            item_count = self.items.count()
            return f"Prescription for {patient_name} - {item_count} medication(s)"
    
    def get_medications(self):
        """Get all medications for this prescription (legacy or new items)"""
        items = self.items.all()
        if items.exists():
            return items
        elif self.medication:  # Legacy single medication
            # Return as list for template compatibility
            return [{
                'medication': self.medication,
                'dosage': self.dosage,
                'frequency': self.frequency,
                'duration': self.duration,
                'quantity': self.quantity,
                'is_legacy': True
            }]
        return []


class PrescriptionItem(models.Model):
    """Individual medication items in a prescription (supports multiple medications)"""
    prescription = models.ForeignKey(Prescription, related_name='items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medication.name} - {self.dosage}"
    
    class Meta:
        ordering = ['id']


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
    
    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.medication.name} - Qty: {self.quantity}"

