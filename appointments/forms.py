from django import forms
from .models import Appointment, Service, TreatmentSession, NutritionConsultation
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'service', 'provider', 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'provider': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter providers to only show doctors, nutritionists, and physiotherapists
        self.fields['provider'].queryset = User.objects.filter(
            role__in=['doctor', 'nutritionist', 'physiotherapist'], is_active=True
        )
        self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

class TreatmentSessionForm(forms.ModelForm):
    class Meta:
        model = TreatmentSession
        fields = [
            'chief_complaint', 'assessment_findings', 'treatment_provided', 'patient_response',
            'pain_level_before', 'pain_level_after', 'functional_improvement',
            'home_exercises', 'recommendations', 'next_appointment_notes', 'session_completed'
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assessment_findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'treatment_provided': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'patient_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pain_level_before': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'pain_level_after': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'functional_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'home_exercises': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_appointment_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'session_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class NutritionConsultationForm(forms.ModelForm):
    class Meta:
        model = NutritionConsultation
        fields = [
            'current_diet', 'dietary_restrictions', 'health_goals',
            'current_weight', 'target_weight', 'body_fat_percentage',
            'meal_plan', 'supplements', 'lifestyle_recommendations',
            'follow_up_weeks', 'consultation_completed'
        ]
        widgets = {
            'current_diet': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'dietary_restrictions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'health_goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'kg'}),
            'target_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'kg'}),
            'body_fat_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '%'}),
            'meal_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'supplements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lifestyle_recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'follow_up_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 52}),
            'consultation_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
