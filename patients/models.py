from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class PatientGroup(models.Model):
    """Groups for categorizing patients (e.g. Corporate, Insurance, VIP, Walk-in)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_is_active_display(self):
        return 'Active' if self.is_active else 'Inactive'

    class Meta:
        ordering = ['name']
        verbose_name = 'Patient Group'
        verbose_name_plural = 'Patient Groups'


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    ID_TYPE_CHOICES = [
        ('NATIONAL', 'National ID'),
        ('DRIVERS', 'Driver\'s License'),
        ('PASSPORT', 'Passport'),
        ('VOTER', 'Voter\'s ID'),
        ('OTHER', 'Other'),
    ]
    
    VISIT_REASON_CHOICES = [
        ('CONSULTATION', 'General Consultation'),
        ('CHECKUP', 'Routine Checkup'),
        ('EMERGENCY', 'Emergency'),
        ('FOLLOWUP', 'Follow-up Visit'),
        ('REFERRAL', 'Referral'),
        ('TREATMENT', 'Treatment'),
        ('SCREENING', 'Screening'),
        ('OTHER', 'Other'),
    ]
    
    # Personal Information
    patient_id = models.CharField(max_length=20, unique=True)
    is_visiting_patient = models.BooleanField(default=False, help_text="Check if this is a visiting patient with minimal information")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True)
    
    # Identification Information
    id_type = models.CharField(max_length=10, choices=ID_TYPE_CHOICES, blank=True, help_text="Type of identification document")
    id_number = models.CharField(max_length=50, blank=True, help_text="Identification document number")
    
    # Visit Information
    reason_for_visit = models.CharField(max_length=20, choices=VISIT_REASON_CHOICES, blank=True, help_text="Reason for current visit")
    
    # Address Information
    address_line1 = models.CharField(max_length=100, blank=True)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, default='USA', blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Referring Doctor
    referring_doctor_name = models.CharField(max_length=100, blank=True, help_text="Name of the referring doctor")
    referring_doctor_location = models.CharField(max_length=200, blank=True, help_text="Location / clinic of the referring doctor")
    referring_doctor_contact = models.CharField(max_length=100, blank=True, help_text="Phone or email of the referring doctor")

    # Medical Information
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True, help_text="List any known allergies")
    medical_history = models.TextField(blank=True, help_text="Previous medical conditions")
    current_medications = models.TextField(blank=True, help_text="Current medications")
    
    # Insurance Information
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    insurance_group_number = models.CharField(max_length=50, blank=True)
    
    # Patient Group
    patient_group = models.ForeignKey(
        PatientGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patients', help_text="Assign patient to a group for differential pricing"
    )

    # System Information
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    registration_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.is_visiting_patient and not (self.first_name and self.last_name):
            return f"Visiting Patient ({self.patient_id})"
        return f"{self.first_name} {self.last_name} ({self.patient_id})"
    
    def get_full_name(self):
        if self.is_visiting_patient and not (self.first_name and self.last_name):
            return "Visiting Patient"
        return f"{self.first_name} {self.last_name}"
    
    def has_complete_name(self):
        """Check if patient has both first and last name"""
        return bool(self.first_name and self.last_name)
    
    def get_age(self):
        if not self.date_of_birth:
            return "Unknown"
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    class Meta:
        ordering = ['last_name', 'first_name']

class VitalSigns(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_date = models.DateTimeField(auto_now_add=True)
    
    # Vital measurements
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    blood_pressure_systolic = models.IntegerField(blank=True, null=True, help_text="Systolic BP")
    blood_pressure_diastolic = models.IntegerField(blank=True, null=True, help_text="Diastolic BP")
    heart_rate = models.IntegerField(blank=True, null=True, help_text="Heart rate (BPM)")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Temperature in Celsius")
    respiratory_rate = models.IntegerField(blank=True, null=True, help_text="Breaths per minute")
    oxygen_saturation = models.IntegerField(help_text="SpO2 percentage", blank=True, null=True)
    
    # Physical Examination fields
    eyes_rt = models.CharField(max_length=100, blank=True, default='', help_text="Right eye exam")
    eyes_lt = models.CharField(max_length=100, blank=True, default='', help_text="Left eye exam")
    ears_rt = models.CharField(max_length=100, blank=True, default='', help_text="Right ear exam")
    ears_lt = models.CharField(max_length=100, blank=True, default='', help_text="Left ear exam")
    cardiovascular = models.CharField(max_length=100, blank=True, default='', help_text="Cardiovascular exam")
    heart = models.CharField(max_length=100, blank=True, default='', help_text="Heart exam")
    lungs = models.CharField(max_length=100, blank=True, default='', help_text="Lungs exam")
    chest_xray = models.CharField(max_length=100, blank=True, default='', help_text="Chest X-Ray findings")
    respiratory_exam = models.CharField(max_length=100, blank=True, default='', help_text="Respiratory exam")
    gi_abdomen = models.CharField(max_length=100, blank=True, default='', help_text="GI/Abdomen exam")
    cns = models.CharField(max_length=100, blank=True, default='', help_text="CNS exam")
    psychiatry = models.CharField(max_length=100, blank=True, default='', help_text="Psychiatry exam")
    extremities = models.CharField(max_length=100, blank=True, default='', help_text="Extremities exam")
    skin = models.CharField(max_length=100, blank=True, default='', help_text="Skin exam")
    deformities = models.CharField(max_length=100, blank=True, default='', help_text="Deformities")
    hernia = models.CharField(max_length=100, blank=True, default='', help_text="Hernia exam")
    varicose_veins = models.CharField(max_length=100, blank=True, default='', help_text="Varicose veins exam")
    venereal_diseases = models.CharField(max_length=100, blank=True, default='', help_text="Venereal diseases exam")
    
    # Additional measurements
    bmi = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        # Calculate BMI automatically
        if self.height and self.weight:
            height_m = float(self.height) / 100  # Convert cm to meters
            self.bmi = round(float(self.weight) / (height_m ** 2), 1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Vitals for {self.patient.get_full_name()} on {self.recorded_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-recorded_date']

class LabTest(models.Model):
    """Laboratory test results for patients"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_date = models.DateTimeField(auto_now_add=True)
    
    # Laboratory Tests - Urine
    urine_sugar = models.CharField(max_length=100, blank=True, default='', help_text="Urine Sugar")
    urine_albumin = models.CharField(max_length=100, blank=True, default='', help_text="Urine Albumin")
    urine_bilharziasis = models.CharField(max_length=100, blank=True, default='', help_text="Urine Bilharziasis")
    
    # Laboratory Tests - Stool/Routine
    stool_helminthes = models.CharField(max_length=100, blank=True, default='', help_text="Stool Helminthes")
    stool_giardia = models.CharField(max_length=100, blank=True, default='', help_text="Stool Giardia")
    stool_bilharziasis = models.CharField(max_length=100, blank=True, default='', help_text="Stool Bilharziasis")
    stool_culture_salmonella = models.CharField(max_length=100, blank=True, default='', help_text="Culture Salmonella/Shigella")
    stool_v_cholerae = models.CharField(max_length=100, blank=True, default='', help_text="V. Cholerae")
    
    # Laboratory Tests - Blood
    blood_haemoglobin = models.CharField(max_length=100, blank=True, default='', help_text="Haemoglobin")
    blood_malaria = models.CharField(max_length=100, blank=True, default='', help_text="Thick film Malaria")
    blood_micro_filaria = models.CharField(max_length=100, blank=True, default='', help_text="Micro Filaria")
    
    # Laboratory Tests - Chemistry
    chemistry_fbs = models.CharField(max_length=100, blank=True, default='', help_text="F.B.S (Fasting Blood Sugar)")
    chemistry_lfts = models.CharField(max_length=100, blank=True, default='', help_text="L.F.T.S (Liver Function Tests)")
    chemistry_kfts = models.CharField(max_length=100, blank=True, default='', help_text="KFTS (Kidney Function Tests)")
    
    # Laboratory Tests - Elisa
    elisa_hcv_ab = models.CharField(max_length=100, blank=True, default='', help_text="HCV Ab")
    elisa_hbs_ag = models.CharField(max_length=100, blank=True, default='', help_text="Hbs Ag")
    elisa_hiv = models.CharField(max_length=100, blank=True, default='', help_text="HIV 1/2 Test")
    
    # Laboratory Tests - Other Tests
    other_blood_group = models.CharField(max_length=100, blank=True, default='', help_text="Blood Group")
    other_pregnancy_test = models.CharField(max_length=100, blank=True, default='', help_text="Pregnancy Test")
    other_vdrl_tpha = models.CharField(max_length=100, blank=True, default='', help_text="VDRL / TPHA")
    
    # Additional notes
    notes = models.TextField(blank=True, help_text="Additional laboratory notes")
    
    def __str__(self):
        return f"Lab Tests for {self.patient.get_full_name()} on {self.recorded_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-recorded_date']
        verbose_name = 'Laboratory Test'
        verbose_name_plural = 'Laboratory Tests'

class Triage(models.Model):
    PRIORITY_CHOICES = [
        ('1', 'Critical - Immediate'),
        ('2', 'High - Within 15 minutes'),
        ('3', 'Medium - Within 30 minutes'),
        ('4', 'Low - Within 60 minutes'),
        ('5', 'Non-urgent - Within 2 hours'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('general', 'General Medicine'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='triages')
    triaged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    triage_date = models.DateTimeField(auto_now_add=True)
    
    # Department routing
    assigned_department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='general')
    
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    pain_scale = models.IntegerField(help_text="Pain scale 0-10", blank=True, null=True)
    priority_level = models.CharField(max_length=1, choices=PRIORITY_CHOICES)
    
    # Basic triage information
    symptoms = models.TextField(help_text="Current symptoms")
    onset = models.CharField(max_length=100, help_text="When did symptoms start?")
    duration = models.CharField(max_length=100, help_text="How long have symptoms persisted?")
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Triage for {self.patient.get_full_name()} - Priority {self.priority_level}"
    
    class Meta:
        ordering = ['-triage_date']

class Assessment(models.Model):
    ASSESSMENT_TYPE_CHOICES = [
        ('first_visit', 'First Visit Assessment'),
        ('follow_up', 'Follow-up Assessment'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('general', 'General Medicine'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='assessments')
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    # Assessment type
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    # Legacy field - kept for backward compatibility
    department = models.CharField(max_length=20, default='general', blank=True)
    
    # Link to appointment
    related_appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    
    # Legacy field - kept for backward compatibility
    related_triage = models.ForeignKey(Triage, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    
    # Assessment details
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    history_of_present_illness = models.TextField(help_text="Detailed history of current condition")
    
    # Physical examination
    physical_examination = models.TextField(help_text="Physical examination findings")
    mobility_status = models.CharField(max_length=100, blank=True)
    mental_status = models.CharField(max_length=100, blank=True)
    
    # Additional clinical findings (optional)
    additional_findings = models.TextField(blank=True, help_text="Any additional clinical observations")
    
    # Clinical findings
    diagnosis = models.TextField(blank=True, help_text="Clinical diagnosis or impression")
    treatment_plan = models.TextField(blank=True, help_text="Recommended treatment plan")
    
    # Follow-up information
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_instructions = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_assessment_type_display()} for {self.patient.get_full_name()} - {self.assessment_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-assessment_date']

# Legacy model - keep for backward compatibility during migration
class TriageAssessment(models.Model):
    PRIORITY_CHOICES = [
        ('1', 'Critical - Immediate'),
        ('2', 'High - Within 15 minutes'),
        ('3', 'Medium - Within 30 minutes'),
        ('4', 'Low - Within 60 minutes'),
        ('5', 'Non-urgent - Within 2 hours'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('general', 'General Medicine'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='triage_assessments')
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    # Department routing
    assigned_department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='general')
    
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    pain_scale = models.IntegerField(help_text="Pain scale 0-10", blank=True, null=True)
    priority_level = models.CharField(max_length=1, choices=PRIORITY_CHOICES)
    
    # Assessment details
    symptoms = models.TextField(help_text="Current symptoms")
    onset = models.CharField(max_length=100, help_text="When did symptoms start?")
    duration = models.CharField(max_length=100, help_text="How long have symptoms persisted?")
    
    # Physical assessment
    mobility_status = models.CharField(max_length=100, blank=True)
    mental_status = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Triage Assessment for {self.patient.get_full_name()} - Priority {self.priority_level}"
    
    class Meta:
        ordering = ['-assessment_date']
