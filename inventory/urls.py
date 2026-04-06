from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Legacy inventory URLs - Use pharmacy app for current inventory management
    path('', views.drug_list, name='drug_list'),
    path('drug/add/', views.drug_edit, name='drug_add'),
    path('drug/<int:pk>/edit/', views.drug_edit, name='drug_edit'),
    path('supplier/add/', views.supplier_edit, name='supplier_add'),
    path('supplier/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('usage/record/', views.record_usage, name='record_usage'),
    path('cashflow/', views.cashflow_list, name='cashflow_list'),
    
    # Sales URLs removed - Now handled by pharmacy app
    # Use pharmacy:sales_dashboard, pharmacy:sales_list, pharmacy:sales_report instead
]
