from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
from calendar import monthrange

from .models import Department, Staff, DutyRoster, ShiftSwapRequest, LeaveRequest, Attendance
from .forms import (
    DepartmentForm, StaffForm, StaffUserCreationForm, DutyRosterForm,
    BulkRosterForm, ShiftSwapRequestForm, ShiftSwapReviewForm,
    LeaveRequestForm, LeaveReviewForm, AttendanceForm
)
from accounts.decorators import admin_required, medical_staff_required


# ==================== DASHBOARD ====================
@login_required
def staff_dashboard(request):
    """Main dashboard for staff management"""
    total_staff = Staff.objects.filter(is_active=True).count()
    departments = Department.objects.filter(is_active=True).annotate(
        active_staff_count=Count('staff', filter=Q(staff__is_active=True))
    )
    
    # Today's roster
    today = timezone.now().date()
    today_shifts = DutyRoster.objects.filter(
        date=today,
        status='scheduled'
    ).select_related('staff', 'department').order_by('shift_start')
    
    # Pending approvals
    pending_leave = LeaveRequest.objects.filter(status='pending').count()
    pending_swaps = ShiftSwapRequest.objects.filter(status='pending').count()
    
    # Recent activity
    recent_leave = LeaveRequest.objects.select_related('staff').order_by('-created_at')[:5]
    recent_swaps = ShiftSwapRequest.objects.select_related(
        'requested_by', 'requested_with'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_staff': total_staff,
        'departments': departments,
        'today_shifts': today_shifts,
        'pending_leave': pending_leave,
        'pending_swaps': pending_swaps,
        'recent_leave': recent_leave,
        'recent_swaps': recent_swaps,
    }
    return render(request, 'staff_management/dashboard.html', context)


# ==================== DEPARTMENT MANAGEMENT ====================
@login_required
@admin_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.annotate(
        active_staff_count=Count('staff', filter=Q(staff__is_active=True))
    ).order_by('name')
    
    context = {'departments': departments}
    return render(request, 'staff_management/department_list.html', context)


@login_required
@admin_required
def department_create_ajax(request):
    """AJAX endpoint for creating departments"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = DepartmentForm(request.POST)
    if form.is_valid():
        department = form.save()
        return JsonResponse({
            'success': True,
            'message': f'Department "{department.name}" created successfully!',
            'department_id': department.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        }, status=400)


# ==================== STAFF MANAGEMENT ====================
@login_required
def staff_list(request):
    """List all staff members"""
    staff_list = Staff.objects.select_related(
        'user', 'department'
    ).filter(is_active=True).order_by('user__first_name')
    
    # Filter by department
    department_id = request.GET.get('department')
    if department_id:
        staff_list = staff_list.filter(department_id=department_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        staff_list = staff_list.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(staff_list, 20)
    page = request.GET.get('page')
    staff = paginator.get_page(page)
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'staff': staff,
        'departments': departments,
        'selected_department': department_id,
        'search_query': search
    }
    return render(request, 'staff_management/staff_list.html', context)


@login_required
def staff_detail(request, pk):
    """View staff member details"""
    staff = get_object_or_404(Staff.objects.select_related('user', 'department'), pk=pk)
    
    # Get upcoming shifts
    upcoming_shifts = DutyRoster.objects.filter(
        staff=staff.user,
        date__gte=timezone.now().date(),
        status='scheduled'
    ).order_by('date', 'shift_start')[:10]
    
    # Get recent attendance
    recent_attendance = Attendance.objects.filter(
        staff=staff.user
    ).order_by('-date')[:10]
    
    # Get leave requests
    leave_requests = LeaveRequest.objects.filter(
        staff=staff.user
    ).order_by('-created_at')[:10]
    
    context = {
        'staff': staff,
        'upcoming_shifts': upcoming_shifts,
        'recent_attendance': recent_attendance,
        'leave_requests': leave_requests,
    }
    return render(request, 'staff_management/staff_detail.html', context)


@login_required
@admin_required
def staff_create(request):
    """Create new staff member"""
    if request.method == 'POST':
        user_form = StaffUserCreationForm(request.POST)
        staff_form = StaffForm(request.POST)
        
        if user_form.is_valid() and staff_form.is_valid():
            user = user_form.save()
            staff = staff_form.save(commit=False)
            staff.user = user
            staff.save()
            
            messages.success(request, f'Staff member {user.get_full_name()} created successfully!')
            return redirect('staff_management:staff_detail', pk=staff.pk)
    else:
        user_form = StaffUserCreationForm()
        staff_form = StaffForm()
    
    context = {
        'user_form': user_form,
        'staff_form': staff_form,
        'title': 'Add New Staff Member'
    }
    return render(request, 'staff_management/staff_form.html', context)


# ==================== DUTY ROSTER ====================
@login_required
def duty_roster_list(request):
    """List duty rosters with filters"""
    rosters = DutyRoster.objects.select_related(
        'staff', 'department'
    ).order_by('-date', 'shift_start')
    
    # Filters
    date_filter = request.GET.get('date')
    if date_filter:
        rosters = rosters.filter(date=date_filter)
    else:
        # Default to current week
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        rosters = rosters.filter(date__range=[week_start, week_end])
    
    staff_filter = request.GET.get('staff')
    if staff_filter:
        rosters = rosters.filter(staff_id=staff_filter)
    
    department_filter = request.GET.get('department')
    if department_filter:
        rosters = rosters.filter(department_id=department_filter)
    
    context = {
        'rosters': rosters,
        'departments': Department.objects.filter(is_active=True),
    }
    return render(request, 'staff_management/duty_roster_list.html', context)


@login_required
def duty_roster_calendar(request):
    """Calendar view of duty roster"""
    # Get month and year from request or use current
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Get rosters for the month
    rosters = DutyRoster.objects.filter(
        date__year=year,
        date__month=month
    ).select_related('staff', 'department').order_by('date', 'shift_start')
    
    # Organize by date
    roster_by_date = {}
    for roster in rosters:
        if roster.date not in roster_by_date:
            roster_by_date[roster.date] = []
        roster_by_date[roster.date].append(roster)
    
    context = {
        'year': year,
        'month': month,
        'roster_by_date': roster_by_date,
        'departments': Department.objects.filter(is_active=True),
    }
    return render(request, 'staff_management/duty_roster_calendar.html', context)


@login_required
@admin_required
def duty_roster_create_ajax(request):
    """AJAX endpoint for creating duty rosters"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = DutyRosterForm(request.POST)
    if form.is_valid():
        roster = form.save(commit=False)
        roster.created_by = request.user
        roster.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Shift scheduled for {roster.staff.get_full_name()} on {roster.date}',
            'roster_id': roster.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        }, status=400)


# ==================== SHIFT SWAP REQUESTS ====================
@login_required
def shift_swap_list(request):
    """List shift swap requests"""
    # Show requests relevant to the user
    swaps = ShiftSwapRequest.objects.filter(
        Q(requested_by=request.user) | Q(requested_with=request.user)
    ).select_related(
        'requested_by', 'requested_with', 'original_shift', 'target_shift'
    ).order_by('-created_at')
    
    # Admin sees all
    if request.user.role == 'admin':
        swaps = ShiftSwapRequest.objects.all().select_related(
            'requested_by', 'requested_with', 'original_shift', 'target_shift'
        ).order_by('-created_at')
    
    context = {'shift_swaps': swaps}
    return render(request, 'staff_management/shift_swap_list.html', context)


@login_required
def shift_swap_create_ajax(request):
    """AJAX endpoint for creating shift swap requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = ShiftSwapRequestForm(request.POST, user=request.user)
    if form.is_valid():
        swap = form.save(commit=False)
        swap.requested_by = request.user
        swap.status = 'pending'
        swap.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Shift swap request submitted successfully!',
            'swap_id': swap.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        }, status=400)


# ==================== LEAVE REQUESTS ====================
@login_required
def leave_request_list(request):
    """List leave requests"""
    # Show user's own requests
    leaves = LeaveRequest.objects.filter(
        staff=request.user
    ).order_by('-created_at')
    
    # Admin sees all
    if request.user.role == 'admin':
        leaves = LeaveRequest.objects.all().select_related(
            'staff', 'reviewed_by'
        ).order_by('-created_at')
    
    context = {'leave_requests': leaves}
    return render(request, 'staff_management/leave_request_list.html', context)


@login_required
def leave_request_create_ajax(request):
    """AJAX endpoint for creating leave requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = LeaveRequestForm(request.POST, request.FILES)
    if form.is_valid():
        leave = form.save(commit=False)
        leave.staff = request.user
        leave.status = 'pending'
        leave.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Leave request for {leave.number_of_days} days submitted successfully!',
            'leave_id': leave.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        }, status=400)


@login_required
@admin_required
def leave_request_review_ajax(request, pk):
    """AJAX endpoint for reviewing leave requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    leave = get_object_or_404(LeaveRequest, pk=pk)
    form = LeaveReviewForm(request.POST, instance=leave)
    
    if form.is_valid():
        leave = form.save(commit=False)
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Leave request {leave.status}!',
            'leave_id': leave.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        }, status=400)


# ==================== ATTENDANCE ====================
@login_required
def attendance_list(request):
    """List attendance records"""
    attendances = Attendance.objects.select_related(
        'staff', 'duty_roster'
    ).order_by('-date')
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        attendances = attendances.filter(date__range=[start_date, end_date])
    else:
        # Default to current month
        today = timezone.now().date()
        first_day = today.replace(day=1)
        attendances = attendances.filter(date__gte=first_day)
    
    # Filter by staff
    staff_filter = request.GET.get('staff')
    if staff_filter:
        attendances = attendances.filter(staff_id=staff_filter)
    
    context = {'attendances': attendances}
    return render(request, 'staff_management/attendance_list.html', context)


@login_required
def attendance_record_ajax(request):
    """AJAX endpoint for recording attendance"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = AttendanceForm(request.POST)
    if form.is_valid():
        attendance = form.save(commit=False)
        attendance.recorded_by = request.user
        attendance.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance recorded for {attendance.staff.get_full_name()}',
            'attendance_id': attendance.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        }, status=400)
