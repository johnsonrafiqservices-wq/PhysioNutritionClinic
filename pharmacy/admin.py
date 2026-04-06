from django.contrib import admin
from django import forms
from .models import Category, Medication, Batch, Supplier, Prescription, PrescriptionItem, StockMovement, StockAlert, PurchaseOrder, PurchaseOrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person', 'email']

class BatchInline(admin.TabularInline):
    model = Batch
    extra = 1
    fields = ['batch_number', 'supplier', 'quantity_remaining', 'cost_price', 'selling_price', 
              'manufacturing_date', 'expiry_date', 'is_active']  # 'branch' removed

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'category', 'strength', 'form', 
                   'manufacturer', 'get_current_stock', 'get_stock_status', 'is_active']
    list_filter = ['category', 'form', 'is_active', 'requires_prescription']
    search_fields = ['name', 'generic_name', 'manufacturer']
    inlines = [BatchInline]
    readonly_fields = ['created_at', 'updated_at']
    
    def get_current_stock(self, obj):
        return obj.current_stock
    get_current_stock.short_description = 'Current Stock'
    
    def get_stock_status(self, obj):
        return 'Low' if obj.low_stock else 'OK'
    get_stock_status.short_description = 'Stock Status'

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'medication', 'supplier', 'quantity_remaining', 
                   'selling_price', 'expiry_date', 'get_status', 'is_active']
    list_filter = ['status', 'is_active', 'supplier']  # 'branch' removed
    search_fields = ['batch_number', 'medication__name', 'invoice_number']
    readonly_fields = ['received_date', 'last_quality_check']
    raw_id_fields = ['medication', 'supplier', 'received_by']  # 'branch' removed
    
    def get_status(self, obj):
        if obj.status == 'quarantine':
            return 'In Quarantine'
        elif obj.is_expired:
            return 'Expired'
        elif obj.is_expiring_soon:
            return 'Expiring Soon'
        return 'Active'
    get_status.short_description = 'Status'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['received_by'].initial = request.user
        return form

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 2  # Show 2 empty forms to add medications
    fields = ['medication', 'dosage', 'frequency', 'duration', 'quantity', 'notes']
    verbose_name = 'Medication'
    verbose_name_plural = 'Medications'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'get_medication_count', 'status', 
                   'prescribed_by', 'prescribed_date', 'dispensed_date']
    list_filter = ['status', 'prescribed_date', 'dispensed_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'items__medication__name']
    readonly_fields = ['prescribed_date', 'dispensed_date']
    raw_id_fields = ['patient', 'prescribed_by', 'dispensed_by']
    inlines = [PrescriptionItemInline]
    
    # Hide legacy single medication fields
    exclude = ['medication', 'dosage', 'frequency', 'duration', 'quantity']
    
    def get_medication_count(self, obj):
        count = obj.items.count()
        if count > 0:
            return f"{count} medication(s)"
        elif obj.medication:  # Legacy
            return f"1 medication (legacy)"
        return "0 medications"
    get_medication_count.short_description = 'Medications'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Only set initial for new prescriptions
            form.base_fields['prescribed_by'].initial = request.user
        return form

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['id', 'batch', 'movement_type', 'quantity', 'reference', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['batch__batch_number', 'batch__medication__name', 'reference']
    readonly_fields = ['created_at']
    raw_id_fields = ['batch', 'created_by']
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of stock movements for audit trail
        return False

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'medication', 'current_stock', 'reorder_level', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['medication__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['medication']
    
    actions = ['mark_as_ordered', 'mark_as_resolved']
    
    def mark_as_ordered(self, request, queryset):
        updated = queryset.update(status='ordered')
        self.message_user(request, f'{updated} alerts marked as ordered.')
    mark_as_ordered.short_description = 'Mark selected alerts as ordered'
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected alerts as resolved'

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['medication', 'quantity', 'unit_price', 'total_price', 'notes']
    readonly_fields = ['total_price']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'order_date', 'expected_delivery', 'status', 'total_amount', 'created_by']
    list_filter = ['status', 'order_date', 'supplier']
    search_fields = ['order_number', 'supplier__name']
    readonly_fields = ['order_date', 'created_at', 'updated_at']
    inlines = [PurchaseOrderItemInline]
    raw_id_fields = ['supplier', 'created_by']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Only set initial for new orders
            form.base_fields['created_by'].initial = request.user
            # Generate order number
            from django.utils import timezone
            last_po = PurchaseOrder.objects.order_by('-id').first()
            next_num = (last_po.id + 1) if last_po else 1
            form.base_fields['order_number'].initial = f"{timezone.now().year}{next_num:05d}"
        return form
