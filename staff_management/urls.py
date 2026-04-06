from django.urls import path
from . import views

app_name = 'staff_management'

urlpatterns = [
    # Dashboard
    path('', views.staff_dashboard, name='dashboard'),
    
    # Department Management
    path('departments/', views.department_list, name='department_list'),
    path('ajax/department/create/', views.department_create_ajax, name='department_create_ajax'),
    
    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    
    # Duty Roster
    path('roster/', views.duty_roster_list, name='duty_roster_list'),
    path('roster/calendar/', views.duty_roster_calendar, name='duty_roster_calendar'),
    path('ajax/roster/create/', views.duty_roster_create_ajax, name='duty_roster_create_ajax'),
    
    # Shift Swaps
    path('shift-swaps/', views.shift_swap_list, name='shift_swap_list'),
    path('ajax/shift-swap/create/', views.shift_swap_create_ajax, name='shift_swap_create_ajax'),
    
    # Leave Requests
    path('leave/', views.leave_request_list, name='leave_request_list'),
    path('ajax/leave/create/', views.leave_request_create_ajax, name='leave_request_create_ajax'),
    path('ajax/leave/<int:pk>/review/', views.leave_request_review_ajax, name='leave_request_review_ajax'),
    
    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('ajax/attendance/record/', views.attendance_record_ajax, name='attendance_record_ajax'),
]
