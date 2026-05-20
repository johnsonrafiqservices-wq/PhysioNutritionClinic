from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientGroup

User = get_user_model()

class TestCategory(models.Model):
	"""Main test categories for laboratory tests"""
	name = models.CharField(max_length=50, unique=True)
	code = models.CharField(max_length=20, unique=True, help_text="Category code for templates")
	description = models.TextField(blank=True)
	display_order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['display_order', 'name']
		verbose_name = 'Test Category'
		verbose_name_plural = 'Test Categories'
	
	def __str__(self):
		return self.name


class LabTest(models.Model):
	"""Available laboratory test types"""
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=50, unique=True, help_text="Unique test code")
	category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='lab_tests')
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	normal_range = models.CharField(max_length=200, blank=True, help_text="Normal reference range")
	sample_type = models.CharField(max_length=100, blank=True, help_text="e.g., Blood, Urine, etc.")
	duration_hours = models.IntegerField(default=24, help_text="Expected turnaround time in hours")
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['name']
		verbose_name = 'Laboratory Test'
		verbose_name_plural = 'Laboratory Tests'
	
	def __str__(self):
		return f"{self.name} ({self.code})"
	
	@property
	def is_profile_test(self):
		return self.profile_id is not None
	
	def get_parameters(self):
		if self.profile:
			return self.profile.get_parameters_ordered()
		return TestParameter.objects.none()

class LabTestRequest(models.Model):
	"""Patient laboratory test requests"""
	STATUS_CHOICES = [
		('requested', 'Requested'),
		('sample_collected', 'Sample Collected'),
		('in_progress', 'In Progress'),
		('completed', 'Completed'),
		('cancelled', 'Cancelled'),
	]
	
	PRIORITY_CHOICES = [
		('routine', 'Routine'),
		('urgent', 'Urgent'),
		('stat', 'STAT'),
	]
	
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_requests')
	test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='requests')
	requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_requests_made')
	date_requested = models.DateTimeField(default=timezone.now)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='routine')
	reason_for_test = models.TextField(blank=True, help_text="Reason/indication for requesting this test")
	clinical_notes = models.TextField(blank=True, help_text="Additional clinical notes")
	samples_required = models.CharField(max_length=200, blank=True, help_text="Sample types required (e.g., Blood, Urine, Stool)")
	sample_collected_at = models.DateTimeField(null=True, blank=True)
	sample_id = models.CharField(max_length=50, blank=True)
	certificate_pdf_url = models.URLField(blank=True, help_text="Cloudinary URL for published certificate PDF")
	certificate_gdrive_url = models.URLField(blank=True, help_text="Google Drive URL for published certificate PDF")
	report_pdf_url = models.URLField(blank=True, help_text="Cloudinary URL for published report PDF")
	report_gdrive_url = models.URLField(blank=True, help_text="Google Drive URL for published report PDF")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-date_requested']
		verbose_name = 'Lab Test Request'
		verbose_name_plural = 'Lab Test Requests'
	
	def __str__(self):
		return f"{self.test.name} for {self.patient} ({self.get_status_display()})"

class ParameterCategory(models.Model):
	"""Parameter categories for grouping test parameters"""
	name = models.CharField(max_length=50, unique=True)
	code = models.CharField(max_length=20, unique=True, help_text="Category code for templates")
	description = models.TextField(blank=True)
	display_order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['display_order', 'name']
		verbose_name = 'Parameter Category'
		verbose_name_plural = 'Parameter Categories'
	
	def __str__(self):
		return self.name

class TestParameter(models.Model):
	"""Individual test parameters"""
	RESULT_TYPES = [
		('numeric', 'Numeric'),
		('text', 'Text'),
		('positive_negative', 'Positive/Negative'),
		('reactive_nonreactive', 'Reactive/Non-reactive'),
		('present_absent', 'Present/Absent'),
		('detected_not_detected', 'Detected/Not Detected'),
		('normal_abnormal', 'Normal/Abnormal'),
		('yes_no', 'Yes/No'),
		('grade', 'Grade (1+, 2+, 3+, 4+)'),
		('titer', 'Titer'),
		('percentage', 'Percentage'),
		('ratio', 'Ratio'),
		('custom', 'Custom Options'),
	]
	
	FLAG_CRITERIA = [
		('none', 'No Flagging'),
		('range', 'Reference Range'),
		('positive_negative', 'Positive/Negative'),
		('reactive_nonreactive', 'Reactive/Non-reactive'),
		('present_absent', 'Present/Absent'),
		('detected_not_detected', 'Detected/Not Detected'),
		('normal_abnormal', 'Normal/Abnormal'),
		('custom', 'Custom Logic'),
	]
	
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=50, help_text="Parameter code for reporting")
	description = models.TextField(blank=True)
	category = models.ForeignKey(ParameterCategory, on_delete=models.CASCADE, related_name='parameters', null=True, blank=True)
	result_type = models.CharField(max_length=25, choices=RESULT_TYPES, default='numeric')
	unit = models.CharField(max_length=50, blank=True)
	reference_range_min = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
	reference_range_max = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
	reference_range_text = models.CharField(max_length=200, blank=True)
	flag_criteria = models.CharField(max_length=25, choices=FLAG_CRITERIA, default='range')
	critical_low = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
	critical_high = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
	custom_options = models.JSONField(default=dict, blank=True, help_text="Custom options for result types")
	display_order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['display_order', 'name']
		verbose_name = 'Test Parameter'
		verbose_name_plural = 'Test Parameters'
	
	def __str__(self):
		return f"{self.name} ({self.code})"
	
	def get_result_type_display(self):
		for choice in self.RESULT_TYPES:
			if choice[0] == self.result_type:
				return choice[1]
		return self.result_type
	
	def evaluate_flag(self, result_value):
		"""Evaluate if result should be flagged"""
		if self.flag_criteria == 'none':
			return None
		
		if self.flag_criteria == 'range' and self.result_type == 'numeric':
			try:
				value = float(result_value)
				if self.critical_low is not None and value <= self.critical_low:
					return 'critical_low'
				if self.critical_high is not None and value >= self.critical_high:
					return 'critical_high'
				if self.reference_range_min is not None and value < self.reference_range_min:
					return 'low'
				if self.reference_range_max is not None and value > self.reference_range_max:
					return 'high'
				return 'normal'
			except (ValueError, TypeError):
				return None
		
		elif self.flag_criteria == 'positive_negative':
			if result_value.lower() in ['positive', 'reactive', 'present', 'detected', 'abnormal', 'yes']:
				return 'abnormal'
			elif result_value.lower() in ['negative', 'non-reactive', 'absent', 'not detected', 'normal', 'no']:
				return 'normal'
		
		elif self.flag_criteria == 'reactive_nonreactive':
			if result_value.lower() in ['reactive', 'positive']:
				return 'abnormal'
			elif result_value.lower() in ['non-reactive', 'negative']:
				return 'normal'
		
		elif self.flag_criteria == 'present_absent':
			if result_value.lower() in ['present', 'detected', 'positive']:
				return 'abnormal'
			elif result_value.lower() in ['absent', 'not detected', 'negative']:
				return 'normal'
		
		elif self.flag_criteria == 'detected_not_detected':
			if result_value.lower() in ['detected', 'present', 'positive']:
				return 'abnormal'
			elif result_value.lower() in ['not detected', 'absent', 'negative']:
				return 'normal'
		
		elif self.flag_criteria == 'normal_abnormal':
			if result_value.lower() in ['abnormal', 'positive', 'reactive']:
				return 'abnormal'
			elif result_value.lower() in ['normal', 'negative', 'non-reactive']:
				return 'normal'
		
		return None

class TestProfile(models.Model):
	"""Test profiles containing multiple parameters"""
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=50, unique=True, help_text="Unique profile code")
	description = models.TextField(blank=True)
	category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='test_profiles')
	sample_type = models.CharField(max_length=100, blank=True, help_text="e.g., Blood, Urine, etc.")
	duration_hours = models.IntegerField(default=24, help_text="Expected turnaround time in hours")
	price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	parameters = models.ManyToManyField(TestParameter, through='TestProfileParameter')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['name']
		verbose_name = 'Test Profile'
		verbose_name_plural = 'Test Profiles'
	
	def __str__(self):
		return f"{self.name} ({self.code})"
	
	def get_parameters_ordered(self):
		return self.parameters.order_by('testprofileparameter__display_order')
	
	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('admin:laboratory_testprofile_change', args=[self.pk])

class TestProfileParameter(models.Model):
	"""Through model for TestProfile and TestParameter with ordering"""
	profile = models.ForeignKey(TestProfile, on_delete=models.CASCADE)
	parameter = models.ForeignKey(TestParameter, on_delete=models.CASCADE)
	display_order = models.PositiveIntegerField(default=0)
	
	class Meta:
		ordering = ['display_order']
		unique_together = ['profile', 'parameter']
		verbose_name = 'Profile Parameter'
		verbose_name_plural = 'Profile Parameters'

# Add profile field to LabTest after TestProfile is defined
LabTest.add_to_class('profile', models.ForeignKey(TestProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests'))

class LabTestResult(models.Model):
	"""Laboratory test results"""
	request = models.OneToOneField(LabTestRequest, on_delete=models.CASCADE, related_name='result')
	result_value = models.TextField(help_text="Test result value")
	result_unit = models.CharField(max_length=50, blank=True)
	interpretation = models.TextField(blank=True, help_text="Clinical interpretation")
	remarks = models.TextField(blank=True)
	is_abnormal = models.BooleanField(default=False)
	date_reported = models.DateTimeField(default=timezone.now)
	reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_results_reported')
	verified = models.BooleanField(default=False)
	verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_results_verified')
	verified_at = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		ordering = ['-date_reported']
		verbose_name = 'Lab Test Result'
		verbose_name_plural = 'Lab Test Results'
	
	def __str__(self):
		return f"Result for {self.request}"

class ParameterResult(models.Model):
	"""Individual parameter results for a test"""
	test_result = models.ForeignKey(LabTestResult, on_delete=models.CASCADE, related_name='parameter_results')
	parameter = models.ForeignKey(TestParameter, on_delete=models.CASCADE)
	result_value = models.CharField(max_length=500)
	flag = models.CharField(max_length=20, choices=[
		('normal', 'Normal'),
		('low', 'Low'),
		('high', 'High'),
		('critical_low', 'Critical Low'),
		('critical_high', 'Critical High'),
		('abnormal', 'Abnormal'),
		('pending', 'Pending'),
	], default='pending')
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['parameter__display_order', 'parameter__name']
		unique_together = ['test_result', 'parameter']
		verbose_name = 'Parameter Result'
		verbose_name_plural = 'Parameter Results'
	
	def __str__(self):
		return f"{self.parameter.name}: {self.result_value}"
	
	def save(self, *args, **kwargs):
		# Auto-evaluate flag based on parameter criteria
		if self.parameter:
			self.flag = self.parameter.evaluate_flag(self.result_value) or 'pending'
		super().save(*args, **kwargs)


class LabTestPriceGroup(models.Model):
	"""Differential pricing for lab tests based on patient groups"""
	lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='group_prices')
	patient_group = models.ForeignKey(PatientGroup, on_delete=models.CASCADE, related_name='lab_test_prices')
	price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this lab test for this patient group")
	
	class Meta:
		unique_together = ('lab_test', 'patient_group')
		verbose_name = 'Lab Test Price Group'
		verbose_name_plural = 'Lab Test Price Groups'
	
	def __str__(self):
		return f"{self.lab_test.name} – {self.patient_group.name}: {self.price}"

	@property
	def price_difference(self):
		"""Calculate the difference between group price and default test price"""
		return self.price - self.lab_test.price

	@property
	def discount_percentage(self):
		"""Calculate the discount percentage compared to default test price"""
		if self.lab_test.price == 0:
			return 0
		diff = self.lab_test.price - self.price
		return (diff / self.lab_test.price) * 100 if diff > 0 else 0

	@staticmethod
	def get_price_for_patient(lab_test, patient):
		"""
		Get the price for a lab test for a specific patient.
		Returns group-specific price if available, otherwise returns default lab test price.
		"""
		if patient and patient.patient_group_id:
			try:
				entry = LabTestPriceGroup.objects.get(lab_test=lab_test, patient_group=patient.patient_group)
				return entry.price
			except LabTestPriceGroup.DoesNotExist:
				pass
		return lab_test.price
