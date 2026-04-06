from django.urls import path
from . import views
from .views_reports import (
    expiry_alerts, low_stock_alerts, pharmacy_analytics, purchase_order_list
)
from .excel_views import (
    import_medications, import_batches,
    download_medication_template, download_batch_template
)

app_name = 'pharmacy'

urlpatterns = [
    path('', views.pharmacy_list, name='pharmacy_list'),
    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/dashboard/', views.InventoryDashboardView.as_view(), name='inventory_dashboard'),
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/create/', views.medication_create, name='medication_create'),
    path('medications/<int:pk>/', views.medication_detail, name='medication_detail'),
    path('medications/<int:pk>/edit/', views.medication_edit, name='medication_edit'),
    path('medications/toggle-status/', views.medication_toggle_status, name='medication_toggle_status'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('batches/<int:pk>/edit/', views.batch_edit, name='batch_edit'),
    path('batches/toggle-status/', views.batch_toggle_status, name='batch_toggle_status'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/dispense/<int:pk>/', views.dispense_prescription, name='dispense_prescription'),
    path('prescriptions/<int:prescription_id>/print/', views.prescription_print, name='prescription_print'),
    path('prescriptions/<int:prescription_id>/download-pdf/', views.prescription_download_pdf, name='prescription_download_pdf'),
    path('dispense/', views.dispense_prescription, name='dispense'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/toggle-status/', views.supplier_toggle_status, name='supplier_toggle_status'),
    path('stock/', views.stock_movement_list, name='stock_movement_list'),
    path('stock/add/', views.add_stock, name='add_stock'),
    path('stock/report/', views.stock_report, name='stock_report'),
    path('stock/adjustment/<int:batch_id>/', views.stock_adjustment, name='stock_adjustment'),
    path('quality-check/<int:batch_id>/', views.quality_check, name='quality_check'),
    
    # Sales Management
    path('sales/', views.sales_dashboard, name='sales_dashboard'),
    path('sales/list/', views.sales_list, name='sales_list'),
    path('sales/report/', views.sales_report, name='sales_report'),
    path('sales/record-ajax/', views.record_sale_ajax, name='record_sale_ajax'),
    path('sales/add-to-invoice-ajax/', views.add_sale_to_invoice_ajax, name='add_sale_to_invoice_ajax'),
    
    # AJAX endpoints
    path('ajax/medication/create/', views.medication_create_ajax, name='medication_create_ajax'),
    path('ajax/medication/<int:pk>/update/', views.medication_update_ajax, name='medication_update_ajax'),
    path('ajax/medications/list/', views.get_medications_ajax, name='get_medications_ajax'),
    path('ajax/batches/list/', views.get_batches_ajax, name='get_batches_ajax'),
    path('ajax/batch/create/', views.batch_create_ajax, name='batch_create_ajax'),
    path('ajax/batch/<int:pk>/update/', views.batch_update_ajax, name='batch_update_ajax'),
    path('ajax/prescription/create/', views.prescription_create_ajax, name='prescription_create_ajax'),
    path('ajax/prescription/<int:pk>/dispense/', views.dispense_prescription_ajax, name='dispense_prescription_ajax'),
    path('ajax/prescription/<int:prescription_id>/total/', views.get_prescription_total_ajax, name='get_prescription_total_ajax'),
    path('ajax/stock/adjustment/<int:batch_id>/', views.stock_adjustment_ajax, name='stock_adjustment_ajax'),
    path('ajax/supplier/create/', views.supplier_create_ajax, name='supplier_create_ajax'),
    path('ajax/supplier/<int:pk>/update/', views.supplier_update_ajax, name='supplier_update_ajax'),
    
    # Reports and analytics
    path('alerts/expiry/', expiry_alerts, name='expiry_alerts'),
    path('alerts/low-stock/', low_stock_alerts, name='low_stock_alerts'),
    path('analytics/', pharmacy_analytics, name='analytics'),
    path('purchase-orders/', purchase_order_list, name='purchase_order_list'),
    
    # Excel Import
    path('import/medications/', import_medications, name='import_medications'),
    path('import/batches/', import_batches, name='import_batches'),
    path('templates/medications/', download_medication_template, name='download_medication_template'),
    path('templates/batches/', download_batch_template, name='download_batch_template'),
]