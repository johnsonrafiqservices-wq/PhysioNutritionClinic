from django import forms
from .models import Patient, PatientGroup, VitalSigns, LabTest, Triage, Assessment, TriageAssessment

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'phone', 'email',
            'id_type', 'id_number', 'reason_for_visit',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'referring_doctor_name', 'referring_doctor_location', 'referring_doctor_contact',
            'blood_type', 'allergies', 'medical_history', 'current_medications',
            'insurance_provider', 'insurance_policy_number', 'insurance_group_number',
            'patient_group'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_type': forms.Select(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID number'}),
            'reason_for_visit': forms.Select(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'referring_doctor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doctor name'}),
            'referring_doctor_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clinic / Hospital'}),
            'referring_doctor_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone or email'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical notes to appear on the report'}),
            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'insurance_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_group_number': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_group': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient_group'].queryset = PatientGroup.objects.filter(is_active=True)
        self.fields['patient_group'].empty_label = "No Group (Default Pricing)"

    def _clean_phone_value(self, value):
        import re
        if value:
            return re.sub(r'[\s\-\(\)]', '', value)
        return value

    def clean_phone(self):
        return self._clean_phone_value(self.cleaned_data.get('phone', ''))

    def clean_emergency_contact_phone(self):
        return self._clean_phone_value(self.cleaned_data.get('emergency_contact_phone', ''))

class VisitingPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'is_visiting_patient', 'gender', 'date_of_birth', 'phone', 'email',
            'id_type', 'id_number', 'reason_for_visit',
            'allergies', 'medical_history', 'current_medications', 'patient_group'
        ]
        widgets = {
            'is_visiting_patient': forms.HiddenInput(attrs={'value': True}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_type': forms.Select(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID number'}),
            'reason_for_visit': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'patient_group': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient_group'].queryset = PatientGroup.objects.filter(is_active=True)
        self.fields['patient_group'].empty_label = "No Group (Default Pricing)"
        # Make all fields optional for visiting patients
        for field in self.fields:
            self.fields[field].required = False

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = [
            'height', 'weight', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation',
            'eyes_rt', 'eyes_lt', 'ears_rt', 'ears_lt', 'cardiovascular', 'heart',
            'lungs', 'chest_xray', 'respiratory_exam', 'gi_abdomen', 'cns',
            'psychiatry', 'extremities', 'skin', 'deformities', 'hernia',
            'varicose_veins', 'venereal_diseases', 'notes'
        ]
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'kg'}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mmHg'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mmHg'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'BPM'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '°C'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'breaths/min'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '%'}),
            'eyes_rt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Right eye'}),
            'eyes_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Left eye'}),
            'ears_rt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Right ear'}),
            'ears_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Left ear'}),
            'cardiovascular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cardiovascular findings'}),
            'heart': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Heart findings'}),
            'lungs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lungs findings'}),
            'chest_xray': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chest X-Ray findings'}),
            'respiratory_exam': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Respiratory findings'}),
            'gi_abdomen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GI/Abdomen findings'}),
            'cns': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNS findings'}),
            'psychiatry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Psychiatry findings'}),
            'extremities': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Extremities findings'}),
            'skin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skin findings'}),
            'deformities': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deformities findings'}),
            'hernia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hernia findings'}),
            'varicose_veins': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Varicose veins findings'}),
            'venereal_diseases': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venereal diseases findings'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = [
            'urine_sugar', 'urine_albumin', 'urine_bilharziasis',
            'stool_helminthes', 'stool_giardia', 'stool_bilharziasis', 
            'stool_culture_salmonella', 'stool_v_cholerae',
            'blood_haemoglobin', 'blood_malaria', 'blood_micro_filaria',
            'chemistry_fbs', 'chemistry_lfts', 'chemistry_kfts',
            'elisa_hcv_ab', 'elisa_hbs_ag', 'elisa_hiv',
            'other_blood_group', 'other_pregnancy_test', 'other_vdrl_tpha',
            'notes'
        ]
        widgets = {
            # Urine Tests
            'urine_sugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NIL'}),
            'urine_albumin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NIL'}),
            'urine_bilharziasis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NIL'}),
            # Stool Tests
            'stool_helminthes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NIL'}),
            'stool_giardia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NIL'}),
            'stool_bilharziasis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NIL'}),
            'stool_culture_salmonella': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            'stool_v_cholerae': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            # Blood Tests
            'blood_haemoglobin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 13.8 g/dl'}),
            'blood_malaria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., No Parasites Seen'}),
            'blood_micro_filaria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            # Chemistry Tests
            'chemistry_fbs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3.9 mmol/L'}),
            'chemistry_lfts': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Normal Range'}),
            'chemistry_kfts': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Normal Range'}),
            # Elisa Tests
            'elisa_hcv_ab': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            'elisa_hbs_ag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            'elisa_hiv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            # Other Tests
            'other_blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., O Rhesus Positive'}),
            'other_pregnancy_test': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            'other_vdrl_tpha': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Negative'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TriageForm(forms.ModelForm):
    class Meta:
        model = Triage
        fields = [
            'chief_complaint', 'pain_scale', 'priority_level', 'assigned_department', 'symptoms',
            'onset', 'duration', 'notes'
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pain_scale': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'priority_level': forms.Select(attrs={'class': 'form-control'}),
            'assigned_department': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'onset': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 hours ago'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ongoing for 3 days'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# DEPRECATED: Specialized assessment forms removed in favor of general AssessmentForm
# Use AssessmentForm for all patient assessments
"""
class PhysiotherapyAssessmentForm(forms.ModelForm):
    # Additional physiotherapy-specific fields
    affected_body_parts = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'affected_body_parts'}),
        required=False,
        help_text="Body parts selected on diagram"
    )
    pain_location = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe pain location and characteristics'}),
        required=False
    )
    range_of_motion = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Document range of motion limitations'}),
        required=False
    )
    muscle_strength = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Assess muscle strength (0-5 scale)'}),
        required=False
    )
    functional_assessment = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Activities of daily living, mobility, balance'}),
        required=False
    )
    posture_analysis = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Postural abnormalities and alignment'}),
        required=False
    )
    special_tests = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Orthopedic tests performed and results'}),
        required=False
    )
    
    class Meta:
        model = Assessment
        fields = [
            'assessment_type', 'related_triage', 'chief_complaint', 
            'history_of_present_illness', 'affected_body_parts', 'pain_location',
            'physical_examination', 'range_of_motion', 'muscle_strength', 
            'functional_assessment', 'posture_analysis', 'special_tests',
            'mobility_status', 'diagnosis', 'treatment_plan', 
            'follow_up_required', 'follow_up_date', 'follow_up_instructions', 'notes'
        ]
        widgets = {
            'assessment_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'related_triage': forms.Select(attrs={'class': 'form-control'}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'history_of_present_illness': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'physical_examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'mobility_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ambulatory, wheelchair, assistive devices'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'follow_up_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure required fields are marked as required
        self.fields['assessment_type'].required = True
        self.fields['chief_complaint'].required = True
        
        # Make related_triage optional (legacy field)
        self.fields['related_triage'].required = False
        
        # Add help text for required fields
        self.fields['assessment_type'].help_text = "Required: Select the type of assessment"
        self.fields['chief_complaint'].help_text = "Required: Primary reason for this visit"

class NutritionAssessmentForm(forms.ModelForm):
    # Additional nutrition-specific fields
    dietary_history = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Current eating patterns, food preferences, restrictions'}),
        required=False
    )
    anthropometric_measurements = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Height, weight, BMI, body composition, waist circumference'}),
        required=False
    )
    biochemical_data = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Lab values, blood glucose, lipids, vitamins, minerals'}),
        required=False
    )
    clinical_signs = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Physical signs of nutritional deficiency or excess'}),
        required=False
    )
    food_allergies_intolerances = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Known food allergies, intolerances, sensitivities'}),
        required=False
    )
    nutritional_goals = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Weight management, disease management, performance goals'}),
        required=False
    )
    meal_planning = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Meal plan recommendations, portion sizes, timing'}),
        required=False
    )
    
    class Meta:
        model = Assessment
        fields = [
            'assessment_type', 'related_triage', 'chief_complaint', 
            'dietary_history', 'anthropometric_measurements',
            'clinical_signs', 'food_allergies_intolerances',
            'physical_examination', 'nutritional_goals', 'diagnosis',
            'treatment_plan', 'follow_up_required', 'follow_up_date', 
            'follow_up_instructions', 'notes'
        ]
        widgets = {
            'assessment_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'related_triage': forms.Select(attrs={'class': 'form-control'}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'physical_examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure required fields are marked as required
        self.fields['assessment_type'].required = True
        self.fields['chief_complaint'].required = True
        
        # Make related_triage optional (legacy field)
        self.fields['related_triage'].required = False
        
        # Mark optional fields as not required
        self.fields['diagnosis'].required = False
        self.fields['treatment_plan'].required = False
        self.fields['follow_up_required'].required = False
        self.fields['follow_up_date'].required = False
        self.fields['follow_up_instructions'].required = False
        
        # Add help text for required fields
        self.fields['assessment_type'].help_text = "Required: Select the type of assessment"
        self.fields['chief_complaint'].help_text = "Required: Primary reason for this visit"
"""

# General assessment form - used for all patient assessments
class AssessmentForm(forms.ModelForm):
    """Simplified General Assessment Form - Used for all patient assessments"""
    class Meta:
        model = Assessment
        fields = [
            'assessment_type', 'chief_complaint', 'history_of_present_illness', 
            'physical_examination', 'mobility_status', 'mental_status', 
            'additional_findings', 'diagnosis', 'treatment_plan', 
            'follow_up_required', 'follow_up_date', 'follow_up_instructions', 'notes'
        ]
        widgets = {
            'assessment_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True, 'placeholder': 'Primary reason for visit'}),
            'history_of_present_illness': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed history of current condition'}),
            'physical_examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Physical examination findings'}),
            'mobility_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient mobility status'}),
            'mental_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient mental status'}),
            'additional_findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional clinical observations'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical diagnosis or impression'}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Recommended treatment plan'}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'follow_up_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Follow-up instructions'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure required fields are marked as required
        self.fields['assessment_type'].required = True
        self.fields['chief_complaint'].required = True
        
        # Add help text for required fields
        self.fields['assessment_type'].help_text = "Required: Select the type of assessment (First Visit or Follow-up)"
        self.fields['chief_complaint'].help_text = "Required: Primary reason for this visit"

# Legacy form - keep for backward compatibility
class TriageAssessmentForm(forms.ModelForm):
    class Meta:
        model = TriageAssessment
        fields = [
            'chief_complaint', 'pain_scale', 'priority_level', 'assigned_department', 'symptoms',
            'onset', 'duration', 'mobility_status', 'mental_status', 'notes'
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pain_scale': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'priority_level': forms.Select(attrs={'class': 'form-control'}),
            'assigned_department': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'onset': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 hours ago'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ongoing for 3 days'}),
            'mobility_status': forms.TextInput(attrs={'class': 'form-control'}),
            'mental_status': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
