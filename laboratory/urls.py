from django.urls import path
from . import views
from . import pricing_views

app_name = 'laboratory'

urlpatterns = [
    # Dashboard
    path('', views.laboratory_dashboard, name='dashboard'),
    
    # Lab Test Pricing by Group
    path('test-pricing/', pricing_views.lab_test_price_group_list, name='lab_test_price_group_list'),
    path('test-pricing/set/', pricing_views.lab_test_price_group_set, name='lab_test_price_group_set'),
    path('test-pricing/delete/', pricing_views.lab_test_price_group_delete, name='lab_test_price_group_delete'),
    
    # Test Management
    path('tests/', views.labtest_list, name='labtest_list'),
    path('tests/add/', views.labtest_add, name='labtest_add'),
    path('tests/<int:pk>/', views.labtest_detail, name='labtest_detail'),
    path('tests/<int:pk>/json/', views.labtest_get_json, name='labtest_get_json'),
    path('tests/<int:pk>/edit/', views.labtest_edit, name='labtest_edit'),
    path('tests/<int:pk>/toggle-active/', views.labtest_toggle_active, name='labtest_toggle_active'),
    path('tests/<int:pk>/usage-report/', views.test_usage_report, name='test_usage_report'),
    path('tests/<int:pk>/requests-results/', views.test_requests_results, name='test_requests_results'),
    
    # Test Parameters
    path('parameters/', views.test_parameter_list, name='test_parameter_list'),
    path('parameters/add/', views.test_parameter_add, name='test_parameter_add'),
    path('parameters/<int:pk>/edit/', views.test_parameter_edit, name='test_parameter_edit'),
    
    # Test Profiles
    path('profiles/', views.test_profile_list, name='test_profile_list'),
    path('profiles/add/', views.test_profile_add, name='test_profile_add'),
    path('profiles/<int:pk>/', views.test_profile_detail, name='test_profile_detail'),
    path('profiles/<int:pk>/edit/', views.test_profile_edit, name='test_profile_edit'),
    path('profiles/<int:pk>/add-parameter/', views.test_profile_add_parameter, name='test_profile_add_parameter'),
    path('profiles/<int:pk>/remove-parameter/<int:parameter_pk>/', views.test_profile_remove_parameter, name='test_profile_remove_parameter'),
    path('profiles/<int:pk>/reorder/', views.test_profile_reorder_parameters, name='test_profile_reorder_parameters'),
    
    # Test Requests
    path('requests/', views.request_list, name='request_list'),
    path('requests/export/', views.export_requests, name='export_requests'),
    path('requests/create/', views.labtest_request, name='labtest_request'),
    path('requests/create-bulk/', views.labtest_request_bulk, name='labtest_request_bulk'),
    path('requests/price-preview/', views.get_price_preview, name='get_price_preview'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/print/', views.request_print, name='request_print'),
    path('requests/<int:pk>/report/', views.test_report, name='test_report'),
    path('requests/<int:pk>/certificate/', views.test_certificate, name='test_certificate'),
    path('patient/<str:patient_id>/certificate/', views.test_certificate_patient, name='test_certificate_patient'),
    path('requests/<int:pk>/update-status/', views.update_request_status, name='update_request_status'),
    path('requests/<int:pk>/publish-certificate/', views.publish_certificate, name='publish_certificate'),
    path('requests/<int:pk>/publish-report/', views.publish_report, name='publish_report'),
    path('requests/batch-export/', views.batch_export_reports, name='batch_export_reports'),
    path('requests/batch-export-pdf/', views.batch_export_reports_pdf, name='batch_export_reports_pdf'),
    path('requests/batch-upload/', views.batch_upload_reports, name='batch_upload_reports'),
    
    # Patient Lab Tests JSON (for selection popup)
    path('patient/<str:patient_id>/lab-tests-json/', views.patient_lab_tests_json, name='patient_lab_tests_json'),
    
    # Batch Download Tests
    path('batch-download-tests/', views.batch_download_tests, name='batch_download_tests'),
    
    # Physical Examination Form
    path('physical-exam/<str:patient_id>/', views.physical_exam_form, name='physical_exam_form'),
    
    # Results
    path('results/', views.labtest_results, name='labtest_results'),
    path('results/add/', views.labtest_result_add, name='labtest_result_add'),
    path('results/add/<int:request_id>/', views.labtest_result_add, name='labtest_result_add_for_request'),
    path('requests/<int:request_id>/add-result/', views.add_result_modal, name='add_result_modal'),
    path('requests/<int:request_id>/edit-result/', views.edit_result_modal, name='edit_result_modal'),
    path('result/<int:pk>/', views.result_detail, name='result_detail'),
    path('result/<int:pk>/verify/', views.verify_result, name='verify_result'),
    path('result/<int:pk>/unverify/', views.unverify_result, name='unverify_result'),
]
