from django.contrib import admin
from .models import Patient, PatientGroup, VitalSigns, Triage, Assessment, TriageAssessment


@admin.register(PatientGroup)
class PatientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'first_name', 'last_name', 'date_of_birth', 'age', 'phone', 'registration_date', 'is_active')

    @admin.display(description='Age')
    def age(self, obj):
        return obj.get_age()
    list_filter = ('gender', 'blood_type', 'registration_date', 'is_active', 'patient_group')
    search_fields = ('patient_id', 'first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('registration_date', 'last_updated')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('patient_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'phone', 'email')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Referring Doctor', {
            'fields': ('referring_doctor_name', 'referring_doctor_location', 'referring_doctor_contact')
        }),
        ('Medical Information', {
            'fields': ('blood_type', 'allergies', 'medical_history', 'current_medications')
        }),
        ('Insurance', {
            'fields': ('insurance_provider', 'insurance_policy_number', 'insurance_group_number')
        }),
        ('Patient Group', {
            'fields': ('patient_group',)
        }),
        ('System Information', {
            'fields': ('registered_by', 'registration_date', 'last_updated', 'is_active')
        }),
    )

@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ('patient', 'recorded_date', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 'temperature', 'bmi')
    list_filter = ('recorded_date', 'recorded_by')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id')
    readonly_fields = ('recorded_date', 'bmi')

@admin.register(Triage)
class TriageAdmin(admin.ModelAdmin):
    list_display = ('patient', 'triage_date', 'priority_level', 'assigned_department', 'chief_complaint', 'triaged_by')
    list_filter = ('priority_level', 'assigned_department', 'triage_date', 'triaged_by')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id', 'chief_complaint')
    readonly_fields = ('triage_date',)
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'triaged_by', 'triage_date')
        }),
        ('Triage Details', {
            'fields': ('assigned_department', 'priority_level', 'chief_complaint', 'pain_scale')
        }),
        ('Symptoms & History', {
            'fields': ('symptoms', 'onset', 'duration')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'assessment_date', 'assessment_type', 'department', 'assessed_by')
    list_filter = ('assessment_type', 'department', 'assessment_date', 'assessed_by', 'follow_up_required')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id', 'chief_complaint', 'diagnosis')
    readonly_fields = ('assessment_date',)
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'assessed_by', 'assessment_date')
        }),
        ('Assessment Details', {
            'fields': ('assessment_type', 'department', 'related_triage', 'chief_complaint')
        }),
        ('Clinical Information', {
            'fields': ('history_of_present_illness', 'physical_examination', 'mobility_status', 'mental_status')
        }),
        ('Diagnosis & Treatment', {
            'fields': ('diagnosis', 'treatment_plan')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date', 'follow_up_instructions')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

# Legacy admin - keep for backward compatibility
@admin.register(TriageAssessment)
class TriageAssessmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'assessment_date', 'priority_level', 'chief_complaint', 'assessed_by')
    list_filter = ('priority_level', 'assessment_date', 'assessed_by')
    search_fields = ('patient__first_name', 'patient__last_name', 'chief_complaint')
    readonly_fields = ('assessment_date',)
