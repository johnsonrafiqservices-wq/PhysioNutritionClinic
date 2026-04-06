from django.contrib import admin
from .models import Department, Staff, DutyRoster, ShiftSwapRequest, LeaveRequest, Attendance


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head_of_department', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'position', 'employment_status', 'is_active']
    list_filter = ['is_active', 'employment_status', 'department', 'joining_date']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'position']
    ordering = ['user__first_name', 'user__last_name']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(DutyRoster)
class DutyRosterAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'shift_type', 'shift_start', 'shift_end', 'department', 'status']
    list_filter = ['status', 'shift_type', 'department', 'date']
    search_fields = ['staff__first_name', 'staff__last_name']
    ordering = ['-date', 'shift_start']
    date_hierarchy = 'date'


@admin.register(ShiftSwapRequest)
class ShiftSwapRequestAdmin(admin.ModelAdmin):
    list_display = ['requested_by', 'requested_with', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'staff_approved', 'manager_approved']
    search_fields = ['requested_by__first_name', 'requested_by__last_name', 
                     'requested_with__first_name', 'requested_with__last_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'number_of_days', 'status']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['staff__first_name', 'staff__last_name', 'reason']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'check_in_time', 'check_out_time', 'hours_worked']
    list_filter = ['status', 'date']
    search_fields = ['staff__first_name', 'staff__last_name']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    def hours_worked(self, obj):
        return obj.hours_worked
    hours_worked.short_description = 'Hours Worked'
