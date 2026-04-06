from django import forms
from .models import LabTest, LabTestRequest, LabTestResult, TestParameter, TestProfile, TestProfileParameter, ParameterResult

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['name', 'code', 'category', 'description', 'price', 'currency',
                  'sample_type', 'duration_hours', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Test Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CBC001'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'UGX'}),
            'sample_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Blood, Urine'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LabTestRequestForm(forms.ModelForm):
    class Meta:
        model = LabTestRequest
        fields = ['patient', 'test', 'priority', 'reason_for_test', 'samples_required', 'clinical_notes', 'sample_id']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'test': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'reason_for_test': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason/indication for requesting this test'}),
            'samples_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Blood, Urine, Stool'}),
            'clinical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional clinical notes (optional)'}),
            'sample_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional sample identifier'}),
        }

class LabTestResultForm(forms.ModelForm):
    class Meta:
        model = LabTestResult
        fields = ['request', 'result_value', 'result_unit', 'interpretation', 
                  'remarks', 'is_abnormal']
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'result_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'result_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., g/dL, mg/dL'}),
            'interpretation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_abnormal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TestParameterForm(forms.ModelForm):
    class Meta:
        model = TestParameter
        fields = ['name', 'code', 'description', 'category', 'result_type', 'unit', 
                  'reference_range_min', 'reference_range_max', 'reference_range_text',
                  'flag_criteria', 'critical_low', 'critical_high', 'custom_options',
                  'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parameter Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., HGB, WBC'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'result_type': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., g/dL, mmol/L'}),
            'reference_range_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'reference_range_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'reference_range_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 12-16 g/dL'}),
            'flag_criteria': forms.Select(attrs={'class': 'form-select'}),
            'critical_low': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'critical_high': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'custom_options': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '{"options": ["Option1", "Option2"]}'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TestProfileForm(forms.ModelForm):
    class Meta:
        model = TestProfile
        fields = ['name', 'code', 'description', 'category', 'sample_type', 
                  'duration_hours', 'price', 'currency', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profile Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CMP001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sample_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Blood, Urine'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'UGX'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ParameterResultForm(forms.ModelForm):
    class Meta:
        model = ParameterResult
        fields = ['parameter', 'result_value', 'notes']
        widgets = {
            'parameter': forms.Select(attrs={'class': 'form-select'}),
            'result_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter result value'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        test_result = kwargs.pop('test_result', None)
        super().__init__(*args, **kwargs)
        if test_result and test_result.request.test.is_profile_test:
            # Show only parameters from the test's profile
            self.fields['parameter'].queryset = test_result.request.test.get_parameters()

class ParameterResultFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        test_result = kwargs.pop('test_result', None)
        super().__init__(*args, **kwargs)
        if test_result and test_result.request.test.is_profile_test:
            # Filter parameters for this specific test
            parameters = test_result.request.test.get_parameters()
            for form in self.forms:
                form.fields['parameter'].queryset = parameters

ParameterResultInlineFormSet = forms.inlineformset_factory(
    LabTestResult,
    ParameterResult,
    form=ParameterResultForm,
    formset=ParameterResultFormSet,
    extra=0,
    can_delete=False,
    fields=['parameter', 'result_value', 'notes']
)
