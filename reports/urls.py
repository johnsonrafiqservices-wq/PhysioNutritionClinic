from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('patients/', views.patient_reports, name='patient_reports'),
    path('financial/', views.financial_reports, name='financial_reports'),
    path('appointments/', views.appointment_report, name='appointment_report'),
    path('patients/download/', views.download_patient_report, name='download_patient_report'),
    path('patients/custom/', views.custom_patient_report, name='custom_patient_report'),
    path('patients/custom/download/', views.download_custom_patient_report, name='download_custom_patient_report'),
    path('financial/custom/', views.custom_financial_report, name='custom_financial_report'),
    path('financial/custom/download/', views.download_custom_financial_report, name='download_custom_financial_report'),
    path('financial/download/', views.download_financial_report, name='download_financial_report'),
    path('appointments/custom/', views.custom_appointment_report, name='custom_appointment_report'),
    path('appointments/custom/download/', views.download_custom_appointment_report, name='download_custom_appointment_report'),
    path('department/custom/', views.custom_department_report, name='custom_department_report'),
    path('department/custom/download/', views.download_custom_department_report, name='download_custom_department_report'),
    path('export/', views.export_report, name='export_report'),
    path('audit/', views.audit_log, name='audit_log'),
    path('performance/', views.report_performance, name='report_performance'),
    path('physiotherapy/', views.physiotherapy_reports, name='physiotherapy_reports'),
    path('nutrition/', views.nutrition_reports, name='nutrition_reports'),
    path('clinical-summary/', views.clinical_summary_report, name='clinical_summary_report'),
    path('pharmacy/', views.pharmacy_reports, name='pharmacy_reports'),
    path('laboratory/', views.laboratory_reports, name='laboratory_reports'),
    path('budget-expenses/', views.budget_expense_reports, name='budget_expense_reports'),
]
