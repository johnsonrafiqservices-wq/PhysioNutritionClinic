from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Department, Staff, DutyRoster, ShiftSwapRequest, LeaveRequest, Attendance
from datetime import date, time

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    """Form for creating/editing departments"""
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'head_of_department', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Physiotherapy'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PHYSIO'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'head_of_department': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StaffUserCreationForm(UserCreationForm):
    """Form for creating user accounts for staff"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate role choices from User model
        if hasattr(User, 'ROLE_CHOICES'):
            self.fields['role'].choices = User.ROLE_CHOICES
        
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email


class StaffForm(forms.ModelForm):
    """Form for creating/editing staff profiles"""
    class Meta:
        model = Staff
        fields = [
            'employee_id', 'department', 'position', 'employment_status',
            'joining_date', 'contract_end_date', 'working_hours_per_week',
            'qualifications', 'license_number', 'specialization',
            'emergency_contact_name', 'emergency_contact_phone', 
            'emergency_contact_relationship', 'is_active', 'notes'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., EMP-001'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Physiotherapist'}),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'working_hours_per_week': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DutyRosterForm(forms.ModelForm):
    """Form for creating/editing duty rosters"""
    class Meta:
        model = DutyRoster
        fields = [
            'staff', 'department', 'date', 'shift_type',
            'shift_start', 'shift_end', 'break_start', 'break_end',
            'status', 'notes'
        ]
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shift_type': forms.Select(attrs={'class': 'form-control'}),
            'shift_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'break_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'break_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter staff to only show active staff
        try:
            self.fields['staff'].queryset = User.objects.filter(
                staff_profile__is_active=True
            ).order_by('first_name', 'last_name')
        except:
            pass
    
    def clean(self):
        cleaned_data = super().clean()
        shift_start = cleaned_data.get('shift_start')
        shift_end = cleaned_data.get('shift_end')
        break_start = cleaned_data.get('break_start')
        break_end = cleaned_data.get('break_end')
        
        # Validate break times are within shift times
        if break_start and break_end:
            if break_end <= break_start:
                raise forms.ValidationError('Break end time must be after break start time')
        
        return cleaned_data


class BulkRosterForm(forms.Form):
    """Form for creating multiple roster entries at once"""
    staff_members = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    shift_type = forms.ChoiceField(
        choices=DutyRoster.SHIFT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    shift_start = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    shift_end = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    days_of_week = forms.MultipleChoiceField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter staff to only show active staff
        try:
            self.fields['staff_members'].queryset = User.objects.filter(
                staff_profile__is_active=True
            ).order_by('first_name', 'last_name')
        except:
            pass


class ShiftSwapRequestForm(forms.ModelForm):
    """Form for requesting shift swaps"""
    class Meta:
        model = ShiftSwapRequest
        fields = ['requested_with', 'original_shift', 'target_shift', 'reason']
        widgets = {
            'requested_with': forms.Select(attrs={'class': 'form-control'}),
            'original_shift': forms.Select(attrs={'class': 'form-control'}),
            'target_shift': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please explain why you need this shift swap'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show future shifts for the current user
            self.fields['original_shift'].queryset = DutyRoster.objects.filter(
                staff=user,
                date__gte=timezone.now().date(),
                status='scheduled'
            ).order_by('date', 'shift_start')
            
            # Exclude current user from staff selection
            self.fields['requested_with'].queryset = User.objects.filter(
                staff_profile__is_active=True
            ).exclude(id=user.id).order_by('first_name', 'last_name')
            
            # Only show future shifts
            self.fields['target_shift'].queryset = DutyRoster.objects.filter(
                date__gte=timezone.now().date(),
                status='scheduled'
            ).order_by('date', 'shift_start')
            self.fields['target_shift'].required = False


class ShiftSwapReviewForm(forms.ModelForm):
    """Form for managers to review shift swap requests"""
    class Meta:
        model = ShiftSwapRequest
        fields = ['status', 'manager_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'manager_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LeaveRequestForm(forms.ModelForm):
    """Form for submitting leave requests"""
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'supporting_document']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide reason for leave'}),
            'supporting_document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class LeaveReviewForm(forms.ModelForm):
    """Form for reviewing leave requests"""
    class Meta:
        model = LeaveRequest
        fields = ['status', 'reviewer_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'reviewer_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AttendanceForm(forms.ModelForm):
    """Form for recording attendance"""
    class Meta:
        model = Attendance
        fields = ['staff', 'date', 'status', 'check_in_time', 'check_out_time', 'duty_roster', 'notes']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duty_roster': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
