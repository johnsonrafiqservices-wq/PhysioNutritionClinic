from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceLineItem, Payment, InsuranceClaim, PaymentPlan
from patients.models import Patient
from appointments.models import Service

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'due_date', 'tax_rate', 'discount_amount', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '%'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'UGX 0.00'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
        # Make optional in UI; default to 0 if omitted
        self.fields['tax_rate'].required = False
        self.fields['discount_amount'].required = False
        if not self.fields['tax_rate'].initial:
            self.fields['tax_rate'].initial = 0
        if not self.fields['discount_amount'].initial:
            self.fields['discount_amount'].initial = 0

    def clean(self):
        cleaned = super().clean()
        tax_rate = cleaned.get('tax_rate')
        discount = cleaned.get('discount_amount')
        if tax_rate in (None, ''):
            cleaned['tax_rate'] = 0
        if discount in (None, ''):
            cleaned['discount_amount'] = 0
        return cleaned

class InvoiceLineItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceLineItem
        fields = ['service', 'description', 'quantity', 'unit_price']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control service-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'UGX 0.00'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.all()
        self.fields['service'].empty_label = "Select a service"

# Create formset for invoice line items
InvoiceLineItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceLineItem, 
    form=InvoiceLineItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['patient', 'invoice', 'amount', 'payment_method', 'status', 'reference_number', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'min': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Check number, transaction ID, etc.'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        
        self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
        self.fields['invoice'].queryset = Invoice.objects.filter(status__in=['draft', 'sent', 'overdue'])
        self.fields['invoice'].empty_label = "Select an invoice (optional)"
        self.fields['invoice'].required = False
        
        if invoice:
            # If invoice is provided, hide patient and invoice fields and set them
            self.fields['patient'].widget = forms.HiddenInput()
            self.fields['invoice'].widget = forms.HiddenInput()
            self.fields['patient'].required = False  # Make it not required since it's hidden
            self.fields['invoice'].required = False  # Make it not required since it's hidden
            self.initial['patient'] = invoice.patient.pk
            self.initial['invoice'] = invoice.pk
            
            # Also set the data if this is a bound form
            if hasattr(self, 'data') and self.data:
                self.data = self.data.copy()  # Make it mutable
                self.data['patient'] = str(invoice.patient.pk)
                self.data['invoice'] = str(invoice.pk)
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
    
    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        invoice = cleaned_data.get('invoice')
        amount = cleaned_data.get('amount')
        
        
        # If invoice is provided, ensure patient is also set from the invoice
        if invoice and not patient:
            cleaned_data['patient'] = invoice.patient
            patient = invoice.patient
        
        # If no patient is selected and no invoice is selected, raise error
        if not patient and not invoice:
            raise forms.ValidationError("Either a patient or an invoice must be selected.")
        
        # If invoice is selected, validate payment amount doesn't exceed balance
        if invoice and amount:
            # Check if invoice is already fully paid
            if invoice.status == 'paid':
                raise forms.ValidationError(f"Invoice {invoice.invoice_number} is already fully paid. No additional payment is needed.")
            
            balance_due = invoice.get_balance_due()
            if balance_due <= 0:
                raise forms.ValidationError(f"Invoice {invoice.invoice_number} has no outstanding balance. Current balance: ${balance_due:.2f}")
            
            if amount > balance_due:
                self.add_error('amount', f'Payment amount cannot exceed the balance due of ${balance_due:.2f}')
        
        return cleaned_data

class InsuranceClaimForm(forms.ModelForm):
    class Meta:
        model = InsuranceClaim
        fields = ['patient', 'invoice', 'insurance_provider', 'policy_number', 'group_number', 'claim_amount', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'insurance_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'group_number': forms.TextInput(attrs={'class': 'form-control'}),
            'claim_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
        self.fields['invoice'].queryset = Invoice.objects.filter(status__in=['sent', 'overdue'])
        self.fields['invoice'].empty_label = "Select an invoice"

class PaymentPlanForm(forms.ModelForm):
    class Meta:
        model = PaymentPlan
        fields = ['total_amount', 'monthly_payment', 'number_of_payments', 'start_date', 'notes']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'monthly_payment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'number_of_payments': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
