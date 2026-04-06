from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

class Service(models.Model):
    SERVICE_CATEGORIES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('consultation', 'Consultation'),
        ('assessment', 'Assessment'),
        ('treatment', 'Treatment'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    class Meta:
        ordering = ['category', 'name']

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_provider')
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, help_text="Appointment notes or special instructions")
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.service.name} on {self.appointment_date} at {self.appointment_time}"
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['provider', 'appointment_date', 'appointment_time']

class TreatmentSession(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='treatment_session')
    
    # Session details
    chief_complaint = models.TextField(help_text="Main reason for visit")
    assessment_findings = models.TextField(help_text="Clinical assessment findings")
    treatment_provided = models.TextField(help_text="Treatment/interventions provided")
    patient_response = models.TextField(help_text="Patient's response to treatment")
    
    # Progress tracking
    pain_level_before = models.IntegerField(help_text="Pain scale 0-10 before treatment", blank=True, null=True)
    pain_level_after = models.IntegerField(help_text="Pain scale 0-10 after treatment", blank=True, null=True)
    functional_improvement = models.TextField(blank=True, help_text="Functional improvements noted")
    
    # Plan
    home_exercises = models.TextField(blank=True, help_text="Prescribed home exercises")
    recommendations = models.TextField(blank=True, help_text="Recommendations and advice")
    next_appointment_notes = models.TextField(blank=True, help_text="Notes for next appointment")
    
    # Session completion
    session_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Treatment session for {self.appointment}"
    
    class Meta:
        ordering = ['-appointment__appointment_date']

class NutritionConsultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='nutrition_consultation')
    
    # Assessment
    current_diet = models.TextField(help_text="Current dietary habits")
    dietary_restrictions = models.TextField(blank=True, help_text="Allergies, intolerances, preferences")
    health_goals = models.TextField(help_text="Patient's health and nutrition goals")
    
    # Measurements
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    
    # Plan
    meal_plan = models.TextField(help_text="Recommended meal plan")
    supplements = models.TextField(blank=True, help_text="Recommended supplements")
    lifestyle_recommendations = models.TextField(blank=True, help_text="Lifestyle and activity recommendations")
    
    # Follow-up
    follow_up_weeks = models.IntegerField(default=4, help_text="Recommended follow-up in weeks")
    consultation_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Nutrition consultation for {self.appointment}"
    
    class Meta:
        ordering = ['-appointment__appointment_date']
