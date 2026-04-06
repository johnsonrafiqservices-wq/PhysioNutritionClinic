from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

User = get_user_model()


class Department(models.Model):
    """Department model for organizing staff"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code for department")
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name

    @property
    def staff_count(self):
        return self.staff_set.filter(is_active=True).count()


class Staff(models.Model):
    """Extended staff information linked to User model"""
    EMPLOYMENT_STATUS_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('consultant', 'Consultant'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='staff')
    position = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='full_time')
    joining_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True, help_text="For contract staff")
    
    # Work schedule
    working_hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        validators=[MinValueValidator(0), MaxValueValidator(168)]
    )
    
    # Qualifications
    qualifications = models.TextField(blank=True, help_text="Degrees, certifications, etc.")
    license_number = models.CharField(max_length=50, blank=True, help_text="Professional license number")
    specialization = models.CharField(max_length=100, blank=True)
    
    # Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    @property
    def full_name(self):
        return self.user.get_full_name()


class DutyRoster(models.Model):
    """Duty roster for staff scheduling"""
    SHIFT_TYPE_CHOICES = [
        ('morning', 'Morning Shift (6:00 AM - 2:00 PM)'),
        ('afternoon', 'Afternoon Shift (2:00 PM - 10:00 PM)'),
        ('night', 'Night Shift (10:00 PM - 6:00 AM)'),
        ('day', 'Day Shift (8:00 AM - 5:00 PM)'),
        ('custom', 'Custom Shift'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duty_shifts')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='duty_rosters')
    date = models.DateField()
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES, default='day')
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    
    # Break information
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    
    # Attendance tracking
    actual_start_time = models.TimeField(null=True, blank=True)
    actual_end_time = models.TimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rosters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'shift_start']
        unique_together = ['staff', 'date', 'shift_start']
        verbose_name = 'Duty Roster'
        verbose_name_plural = 'Duty Rosters'

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date} ({self.get_shift_type_display()})"

    @property
    def duration_hours(self):
        """Calculate shift duration in hours"""
        start = datetime.combine(datetime.today(), self.shift_start)
        end = datetime.combine(datetime.today(), self.shift_end)
        if end < start:
            end += timedelta(days=1)
        duration = (end - start).total_seconds() / 3600
        
        # Subtract break time if applicable
        if self.break_start and self.break_end:
            break_start = datetime.combine(datetime.today(), self.break_start)
            break_end = datetime.combine(datetime.today(), self.break_end)
            break_duration = (break_end - break_start).total_seconds() / 3600
            duration -= break_duration
            
        return round(duration, 2)

    @property
    def is_past(self):
        return self.date < timezone.now().date()

    @property
    def is_today(self):
        return self.date == timezone.now().date()

    @property
    def is_future(self):
        return self.date > timezone.now().date()


class ShiftSwapRequest(models.Model):
    """Request for shift swapping between staff members"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved_by_staff', 'Approved by Staff'),
        ('approved_by_manager', 'Approved by Manager'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_swap_requests')
    requested_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_swap_offers')
    
    original_shift = models.ForeignKey(DutyRoster, on_delete=models.CASCADE, related_name='swap_as_original')
    target_shift = models.ForeignKey(DutyRoster, on_delete=models.CASCADE, related_name='swap_as_target', null=True, blank=True)
    
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Approval tracking
    staff_approved = models.BooleanField(default=False)
    staff_approved_at = models.DateTimeField(null=True, blank=True)
    
    manager_approved = models.BooleanField(default=False)
    manager_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_swaps'
    )
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    manager_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shift Swap Request'
        verbose_name_plural = 'Shift Swap Requests'

    def __str__(self):
        return f"Swap: {self.requested_by.get_full_name()} <-> {self.requested_with.get_full_name()}"


class LeaveRequest(models.Model):
    """Staff leave requests and management"""
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('compassionate', 'Compassionate Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('study', 'Study Leave'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_days = models.PositiveIntegerField()
    
    reason = models.TextField()
    supporting_document = models.FileField(upload_to='leave_documents/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date < self.start_date:
            raise ValidationError('End date must be after start date')

    def save(self, *args, **kwargs):
        # Auto-calculate number of days
        if self.start_date and self.end_date:
            self.number_of_days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)


class Attendance(models.Model):
    """Track daily staff attendance"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
    ]

    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # Link to duty roster if applicable
    duty_roster = models.ForeignKey(DutyRoster, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance')
    
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_attendance')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['staff', 'date']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date} ({self.get_status_display()})"

    @property
    def hours_worked(self):
        """Calculate hours worked"""
        if self.check_in_time and self.check_out_time:
            start = datetime.combine(datetime.today(), self.check_in_time)
            end = datetime.combine(datetime.today(), self.check_out_time)
            if end < start:
                end += timedelta(days=1)
            return round((end - start).total_seconds() / 3600, 2)
        return 0
