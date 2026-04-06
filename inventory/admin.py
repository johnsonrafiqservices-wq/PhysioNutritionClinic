from django.contrib import admin
from .models import Drug, Supplier, DrugUsage, CashFlow, Prescription, PrescriptionItem, Dispensing

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'atc_code', 'quantity', 'unit_price', 'expiry_date', 'supplier']
    list_filter = ['supplier', 'expiry_date']
    search_fields = ['name', 'atc_code', 'manufacturer']
    
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'contact', 'email', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'contact', 'email']

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_number', 'patient', 'prescribed_by', 'status', 'date_prescribed']
    list_filter = ['status', 'date_prescribed']
    search_fields = ['prescription_number', 'patient__first_name', 'patient__last_name']
    
@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'drug', 'quantity', 'dosage', 'frequency']
    
@admin.register(Dispensing)
class DispensingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'drug', 'quantity', 'dispensed_by', 'date_dispensed']
    list_filter = ['date_dispensed']
    search_fields = ['patient__first_name', 'patient__last_name', 'drug__name']

@admin.register(DrugUsage)
class DrugUsageAdmin(admin.ModelAdmin):
    list_display = ['drug', 'used_quantity', 'usage_type', 'date_used']
    list_filter = ['usage_type', 'date_used']

@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'currency', 'flow_type', 'date']
    list_filter = ['flow_type', 'date']
