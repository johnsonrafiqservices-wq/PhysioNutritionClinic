from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()


class Supplier(models.Model):
	name = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	contact = models.CharField(max_length=100, blank=True)
	email = models.EmailField(blank=True)
	address = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)
	
	def __str__(self):
		return self.name

class Drug(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	atc_code = models.CharField(max_length=20, blank=True, help_text="WHO ATC code")
	barcode = models.CharField(max_length=50, blank=True)
	manufacturer = models.CharField(max_length=100, blank=True)
	batch_number = models.CharField(max_length=50, blank=True)
	expiry_date = models.DateField(null=True, blank=True)
	quantity = models.PositiveIntegerField(default=0)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	country = models.CharField(max_length=100, blank=True)
	supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name} ({self.atc_code})"


class DrugUsage(models.Model):
	USAGE_TYPE = [
		('internal', 'Internal'),
		('sale', 'Sale'),
	]
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
	used_quantity = models.PositiveIntegerField()
	usage_type = models.CharField(max_length=10, choices=USAGE_TYPE, default='internal')
	used_for = models.CharField(max_length=255, blank=True)
	used_by = models.CharField(max_length=100, blank=True)
	sold_to = models.CharField(max_length=100, blank=True)
	sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	currency = models.CharField(max_length=10, default='UGX')
	country = models.CharField(max_length=100, blank=True)
	date_used = models.DateTimeField(default=timezone.now)

	def __str__(self):
		if self.usage_type == 'sale':
			return f"Sold {self.used_quantity} of {self.drug.name} to {self.sold_to}"
		return f"{self.used_quantity} of {self.drug.name} used by {self.used_by}"


class CashFlow(models.Model):
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	flow_type = models.CharField(max_length=10, choices=[('in', 'In'), ('out', 'Out')])
	description = models.CharField(max_length=255, blank=True)
	country = models.CharField(max_length=100, blank=True)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.flow_type} - {self.amount} {self.currency} ({self.description})"


class Prescription(models.Model):
	"""Medical prescriptions for patients"""
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('dispensed', 'Dispensed'),
		('cancelled', 'Cancelled'),
	]
	
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
	prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescriptions_made')
	prescription_number = models.CharField(max_length=50, unique=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	diagnosis = models.TextField(blank=True)
	notes = models.TextField(blank=True)
	date_prescribed = models.DateTimeField(default=timezone.now)
	date_dispensed = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-date_prescribed']
	
	def save(self, *args, **kwargs):
		if not self.prescription_number:
			# Generate prescription number
			last_rx = Prescription.objects.order_by('-id').first()
			next_num = (last_rx.id + 1) if last_rx else 1
			self.prescription_number = f"RX-{next_num:05d}"
		super().save(*args, **kwargs)
	
	def __str__(self):
		return f"{self.prescription_number} - {self.patient}"


class PrescriptionItem(models.Model):
	"""Individual drugs in a prescription"""
	prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()
	dosage = models.CharField(max_length=100, help_text="e.g., 500mg")
	frequency = models.CharField(max_length=100, help_text="e.g., Twice daily")
	duration = models.CharField(max_length=100, help_text="e.g., 7 days")
	instructions = models.TextField(blank=True)
	
	def __str__(self):
		return f"{self.drug.name} - {self.quantity} units"


class Dispensing(models.Model):
	"""Track drug dispensing to patients"""
	prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True)
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()
	dispensed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	date_dispensed = models.DateTimeField(default=timezone.now)
	notes = models.TextField(blank=True)
	
	class Meta:
		ordering = ['-date_dispensed']
	
	def __str__(self):
		return f"{self.drug.name} - {self.quantity} to {self.patient}"
