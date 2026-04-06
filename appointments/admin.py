from django.contrib import admin
from .models import Service, Appointment, TreatmentSession, NutritionConsultation

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'base_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service', 'provider', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date', 'service__category', 'provider')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id')
    date_hierarchy = 'appointment_date'

@admin.register(TreatmentSession)
class TreatmentSessionAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'session_completed', 'completed_at')
    list_filter = ('session_completed', 'completed_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')

@admin.register(NutritionConsultation)
class NutritionConsultationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'consultation_completed', 'completed_at')
    list_filter = ('consultation_completed', 'completed_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')
