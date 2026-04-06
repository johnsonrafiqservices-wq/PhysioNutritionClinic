from django import forms
from .models import Budget, BudgetItem, Expense, ExpenseCategory


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'icon', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-tag'}),
            'color': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('primary', 'Primary Blue'),
                ('success', 'Success Green'),
                ('danger', 'Danger Red'),
                ('warning', 'Warning Orange'),
                ('info', 'Info Cyan'),
                ('secondary', 'Secondary Gray'),
            ]),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'description', 'period_type', 'start_date', 'end_date', 'total_amount', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'period_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['category', 'allocated_amount', 'notes']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'allocated_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category', 'budget_item', 'description', 'amount', 'currency',
            'expense_date', 'payment_method', 'reference_number', 'vendor_name',
            'notes', 'receipt_file'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'budget_item': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'UGX'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'receipt_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make budget_item optional
        self.fields['budget_item'].required = False
        self.fields['receipt_file'].required = False
        self.fields['reference_number'].required = False
        self.fields['vendor_name'].required = False
        self.fields['notes'].required = False
        
        # Set default currency
        if not self.instance.pk:  # Only for new instances
            self.fields['currency'].initial = 'UGX'


class ExpenseApprovalForm(forms.Form):
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Required if rejecting'})
    )
