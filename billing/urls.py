from django.urls import path
from . import views
from . import pricing_api_views
from . import group_invoice_views

app_name = 'billing'

urlpatterns = [
    path('', views.billing_dashboard, name='billing_dashboard'),
    
    # Group Invoice URLs
    path('group-invoices/', group_invoice_views.group_invoice_list, name='group_invoice_list'),
    path('group-invoices/generate/', group_invoice_views.group_invoice_generate, name='group_invoice_generate'),
    path('group-invoices/<int:pk>/', group_invoice_views.group_invoice_detail, name='group_invoice_detail'),
    path('group-invoices/<int:pk>/print/', group_invoice_views.group_invoice_print, name='group_invoice_print'),
    path('group-invoices/<int:pk>/add-item/', group_invoice_views.group_invoice_add_item, name='group_invoice_add_item'),
    path('group-invoices/<int:pk>/delete-item/<int:item_id>/', group_invoice_views.group_invoice_delete_item, name='group_invoice_delete_item'),
    path('group-invoices/<int:pk>/add-payment/', group_invoice_views.group_invoice_add_payment, name='group_invoice_add_payment'),
    path('group-payments/<int:pk>/receipt/', group_invoice_views.group_payment_receipt, name='group_payment_receipt'),
    
    # Invoice URLs
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/create-for-patient/', views.invoice_create_for_patient, name='invoice_create_for_patient'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/publish/', views.publish_invoice, name='publish_invoice'),
    path('invoices/<int:pk>/status/', views.invoice_status_update, name='invoice_status_update'),
    path('invoices/bulk-action/', views.bulk_invoice_action, name='bulk_invoice_action'),
    path('invoices/aging-report/', views.invoice_aging_report, name='invoice_aging_report'),
    path('invoices/export/csv/', views.export_invoices_csv, name='invoice_export_csv'),
    path('reports/', views.billing_reports, name='billing_reports'),
    path('reports/export/excel/', views.export_billing_excel, name='export_billing_excel'),
    path('patients/<str:patient_id>/draft-invoices/', views.patient_draft_invoices, name='patient_draft_invoices'),
    path('invoices/<int:pk>/send-email/', views.send_invoice_email, name='invoice_send_email'),
    
    # Payment URLs
    path('payments/create/', views.payment_create, name='payment_create'),
    path('invoices/<int:invoice_pk>/payment/', views.payment_create, name='payment_create_for_invoice'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('payments/<int:pk>/publish-receipt/', views.publish_receipt, name='publish_receipt'),
    path('payments/<int:pk>/refund/', views.payment_refund, name='payment_refund'),
    path('payments/export/csv/', views.export_payments_csv, name='payment_export_csv'),
    
    # Insurance Claim URLs
    path('claims/create/', views.insurance_claim_create, name='insurance_claim_create'),
    path('invoices/<int:invoice_pk>/claim/', views.insurance_claim_create, name='insurance_claim_create_for_invoice'),
    path('claims/', views.insurance_claim_list, name='insurance_claim_list'),
    path('claims/<int:pk>/print/', views.insurance_claim_print, name='insurance_claim_print'),
    
    # Payment Plan URLs
    path('payment-plans/', views.payment_plan_list, name='payment_plan_list'),
    path('invoices/<int:invoice_pk>/payment-plan/', views.payment_plan_create, name='payment_plan_create'),
    path('payment-plans/<int:pk>/', views.payment_plan_detail, name='payment_plan_detail'),
    
    # AJAX URLs
    path('ajax/invoices/create-full/', views.invoice_create_full_ajax, name='invoice_create_full_ajax'),
    path('ajax/invoices/create/', views.invoice_create_ajax, name='invoice_create_ajax'),
    path('api/service-price/', views.get_service_price, name='get_service_price'),
    path('ajax/payment/record/', views.payment_record_ajax, name='payment_record_ajax'),
    path('ajax/invoices/for-patient/', views.invoices_for_patient_ajax, name='invoices_for_patient_ajax'),
    path('debug/payment/', views.payment_debug, name='payment_debug'),
    path('test/payment/', views.payment_test, name='payment_test'),
    
    # Pricing API URLs
    path('api/service-price-for-patient/', pricing_api_views.get_service_price_for_patient, name='get_service_price_for_patient'),
    path('api/lab-test-price-for-patient/', pricing_api_views.get_lab_test_price_for_patient, name='get_lab_test_price_for_patient'),
]
