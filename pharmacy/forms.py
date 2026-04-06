from django import forms
from .models import Medication, Batch, Prescription, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem

class QualityCheckForm(forms.Form):
    CONDITION_CHOICES = [
        ('good', 'Good'),
        ('damaged', 'Damaged'),
        ('contaminated', 'Contaminated'),
        ('expired', 'Expired')
    ]
    
    physical_condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        widget=forms.RadioSelect,
        initial='good'
    )
    
    packaging_integrity = forms.BooleanField(
        label='Packaging is intact and sealed',
        initial=True,
        required=False
    )
    
    storage_conditions = forms.BooleanField(
        label='Proper storage conditions maintained',
        initial=True,
        required=False
    )
    
    visual_inspection = forms.BooleanField(
        label='Visual inspection passed',
        initial=True,
        required=False
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='Add any additional observations or concerns'
    )
    
    action_required = forms.BooleanField(
        label='Action required',
        required=False,
        help_text='Check if this batch requires immediate action'
    )
    
    recommended_action = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text='Describe the recommended action if any'
    )



class StockAdjustmentForm(forms.ModelForm):
    ADJUSTMENT_TYPES = [
        ('increase', 'Increase Stock'),
        ('decrease', 'Decrease Stock')
    ]
    
    adjustment_type = forms.ChoiceField(choices=ADJUSTMENT_TYPES)
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    
    class Meta:
        model = StockMovement
        fields = ['quantity', 'adjustment_type', 'reason']
        
    def save(self, commit=True):
        instance = super().save(False)
        instance.movement_type = 'in' if self.cleaned_data['adjustment_type'] == 'increase' else 'out'
        instance.notes = self.cleaned_data['reason']
        instance.reference = f'Stock Adjustment - {self.cleaned_data["adjustment_type"].title()}'
        
        if commit:
            instance.save()
        return instance

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = '__all__'

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            'medication', 'supplier', 'batch_number', 
            'quantity_remaining', 'cost_price', 'selling_price',
            'manufacturing_date', 'expiry_date', 'invoice_number',
            'status', 'is_active', 'notes'
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'manufacturing_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'medication', 'dosage', 'frequency', 'duration', 'quantity', 'instructions']  # Changed from 'visit' to 'patient'

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['batch', 'quantity', 'notes']
        widgets = {
            'batch': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about this stock addition (e.g., PO number, supplier reference)...'
            }),
        }
        
    def save(self, commit=True):
        instance = super().save(False)
        # Force movement_type to 'in' for adding stock
        instance.movement_type = 'in'
        if commit:
            instance.save()
        return instance

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_delivery', 'notes']
        widgets = {
            'expected_delivery': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['medication', 'quantity', 'unit_price', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }