from django import forms
from .models import Drug, DrugUsage, CashFlow, Supplier, Prescription, PrescriptionItem, Dispensing

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'country', 'contact', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = ['name', 'description', 'atc_code', 'barcode', 'manufacturer', 'batch_number', 
                  'expiry_date', 'quantity', 'unit_price', 'currency', 'country', 'supplier']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Drug Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'atc_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WHO ATC Code'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'UGX'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
        }

class DrugUsageForm(forms.ModelForm):
    class Meta:
        model = DrugUsage
        fields = ['drug', 'used_quantity', 'usage_type', 'used_for', 'used_by', 'sold_to', 
                  'sale_price', 'currency', 'country']
        widgets = {
            'drug': forms.Select(attrs={'class': 'form-select'}),
            'used_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'usage_type': forms.Select(attrs={'class': 'form-select'}),
            'used_for': forms.TextInput(attrs={'class': 'form-control'}),
            'used_by': forms.TextInput(attrs={'class': 'form-control'}),
            'sold_to': forms.TextInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'UGX'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = ['drug', 'amount', 'currency', 'flow_type', 'description', 'country']
        widgets = {
            'drug': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'UGX'}),
            'flow_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'diagnosis', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Diagnosis'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes'}),
        }

class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['drug', 'quantity', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'drug': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Twice daily'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class DispensingForm(forms.ModelForm):
    class Meta:
        model = Dispensing
        fields = ['prescription', 'patient', 'drug', 'quantity', 'notes']
        widgets = {
            'prescription': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'drug': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
