from django.urls import path
from . import views
from . import group_views
from . import group_dashboard_views

app_name = 'patients'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.patient_list, name='patient_list'),
    path('register/', views.patient_register, name='patient_register'),
    path('register/visiting/', views.visiting_patient_register, name='visiting_patient_register'),
    path('ajax/register/', views.patient_register_ajax, name='patient_register_ajax'),
    
    # Patient Group Dashboard
    path('group-dashboard/', group_dashboard_views.patient_group_dashboard, name='patient_group_dashboard_home'),
    path('group-dashboard/<int:group_id>/', group_dashboard_views.patient_group_dashboard, name='patient_group_dashboard'),
    
    # Patient Group Management
    path('groups/', group_views.patient_group_list, name='patient_group_list'),
    path('groups/create/', group_views.patient_group_create, name='patient_group_create'),
    path('groups/<int:group_id>/', group_views.patient_group_detail, name='patient_group_detail'),
    path('groups/<int:group_id>/get/', group_views.patient_group_get, name='patient_group_get'),
    path('groups/<int:group_id>/update/', group_views.patient_group_update, name='patient_group_update'),
    path('groups/<int:group_id>/delete/', group_views.patient_group_delete, name='patient_group_delete'),
    path('groups/<int:group_id>/patients/', group_views.group_patients_list, name='group_patients_list'),
    path('groups/assign-patient/', group_views.assign_patient_to_group, name='assign_patient_to_group'),
    
    # Service Price Group Management
    path('service-pricing/', group_views.service_price_group_list, name='service_price_group_list'),
    path('service-pricing/set/', group_views.service_price_group_set, name='service_price_group_set'),
    path('service-pricing/delete/', group_views.service_price_group_delete, name='service_price_group_delete'),
    
    path('<str:patient_id>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('<str:patient_id>/print/', views.patient_details_print, name='patient_details_print'),
    path('<str:patient_id>/vitals/', views.record_vitals, name='record_vitals'),
    path('<str:patient_id>/lab-tests/', views.record_lab_tests, name='record_lab_tests'),
    path('patient/<str:patient_id>/triage/', views.triage_patient, name='triage_patient'),
    path('patient/<str:patient_id>/assessment/', views.assessment_create, name='assessment_create'),
    # DEPRECATED: Specialized assessment URLs removed - use general assessment
    # path('patient/<str:patient_id>/physiotherapy-assessment/', views.physiotherapy_assessment, name='physiotherapy_assessment'),
    # path('patient/<str:patient_id>/nutrition-assessment/', views.nutrition_assessment, name='nutrition_assessment'),
    path('<str:patient_id>/triage-assessment/', views.triage_assessment, name='triage_assessment'),  # Legacy URL
    path('<str:patient_id>/medical-records/', views.patient_medical_records, name='patient_medical_records'),
    path('<str:patient_id>/download-reports/', views.download_all_reports, name='download_all_reports'),
    
    # AJAX-only assessment endpoints
    path('ajax/patient/<str:patient_id>/physiotherapy-assessment/', views.physiotherapy_assessment_ajax, name='physiotherapy_assessment_ajax'),
    path('ajax/patient/<str:patient_id>/nutrition-assessment/', views.nutrition_assessment_ajax, name='nutrition_assessment_ajax'),
    path('ajax/patient/<str:patient_id>/general-assessment/', views.general_assessment_ajax, name='general_assessment_ajax'),
    
    # AJAX-only vital signs and triage endpoints
    path('ajax/<str:patient_id>/vitals/', views.vital_signs_record_ajax, name='vital_signs_record_ajax'),
    path('ajax/vitals/<int:vital_id>/get/', views.vital_signs_get_ajax, name='vital_signs_get_ajax'),
    path('ajax/vitals/<int:vital_id>/update/', views.vital_signs_update_ajax, name='vital_signs_update_ajax'),
    path('ajax/<str:patient_id>/triage/', views.triage_create_ajax, name='triage_create_ajax'),
    
    # Physiotherapist dashboard
    path('physiotherapist/my-patients/', views.physiotherapist_patients, name='physiotherapist_patients'),
    
    # Nutritionist dashboard
    path('nutritionist/my-patients/', views.nutritionist_patients, name='nutritionist_patients'),
]
