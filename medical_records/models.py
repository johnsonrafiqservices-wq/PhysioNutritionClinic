from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient
from appointments.models import Appointment

User = get_user_model()

class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ('assessment', 'Initial Assessment'),
        ('progress', 'Progress Note'),
        ('discharge', 'Discharge Summary'),
        ('referral', 'Referral'),
        ('lab_result', 'Lab Result'),
        ('imaging', 'Imaging Report'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('consent', 'Consent Form'),
        ('intake', 'Intake Form'),
        ('insurance', 'Insurance Document'),
        ('prescription', 'Prescription'),
        ('report', 'Medical Report'),
        ('image', 'Medical Image'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='patient_documents/')
    
    # System fields
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-uploaded_at']
