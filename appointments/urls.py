from django.urls import path
from . import views
from . import service_views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    
    # Service Management
    path('services/', service_views.service_list, name='service_list'),
    path('services/create/', service_views.service_create, name='service_create'),
    path('services/<int:service_id>/get/', service_views.service_get, name='service_get'),
    path('services/<int:service_id>/update/', service_views.service_update, name='service_update'),
    path('services/<int:service_id>/delete/', service_views.service_delete, name='service_delete'),
    
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.calendar_day_detail, name='calendar_day_detail'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/update/', views.appointment_update, name='appointment_update'),
    path('<int:pk>/update-status/', views.appointment_update_status, name='appointment_update_status'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('<int:pk>/reschedule/', views.appointment_reschedule, name='appointment_reschedule'),
    path('<int:appointment_pk>/treatment/', views.treatment_session_create, name='treatment_session_create'),
    path('<int:appointment_pk>/treatment/update/', views.treatment_session_update, name='treatment_session_update'),
    path('<int:appointment_pk>/nutrition/', views.nutrition_consultation_create, name='nutrition_consultation_create'),
    path('<int:appointment_pk>/nutrition/update/', views.nutrition_consultation_update, name='nutrition_consultation_update'),
    path('<int:pk>/confirm/', views.confirm_appointment, name='appointment_confirm'),
    
    # AJAX-only endpoints
    path('ajax/create/', views.appointment_create_ajax, name='appointment_create_ajax'),
    path('ajax/<int:pk>/update/', views.appointment_update_ajax, name='appointment_update_ajax'),
    path('ajax/<int:pk>/cancel/', views.appointment_cancel_ajax, name='appointment_cancel_ajax'),
    path('ajax/<int:pk>/reschedule/', views.appointment_reschedule_ajax, name='appointment_reschedule_ajax'),
    path('ajax/<int:appointment_pk>/treatment/', views.treatment_session_ajax, name='treatment_session_ajax'),
    path('ajax/<int:appointment_pk>/nutrition/', views.nutrition_consultation_ajax, name='nutrition_consultation_ajax'),
]
