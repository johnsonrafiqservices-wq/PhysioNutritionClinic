from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import (
    Invoice, InvoiceLineItem, Payment, InsuranceClaim, PaymentPlan, 
    ServicePriceGroup, BillingAuditLog, GroupInvoice, GroupInvoiceItem, GroupPayment
)


@admin.register(ServicePriceGroup)
class ServicePriceGroupAdmin(admin.ModelAdmin):
    list_display = ('service', 'patient_group', 'price')
    list_filter = ('patient_group', 'service')
    search_fields = ('service__name', 'patient_group__name')
    autocomplete_fields = ['service', 'patient_group']

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'issue_date', 'due_date', 'total_amount', 'status')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('invoice_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at')
    inlines = [InvoiceLineItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'patient', 'due_date', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'patient', 'invoice', 'amount', 'payment_method', 'payment_date', 'status')
    list_filter = ('payment_method', 'status', 'payment_date')
    search_fields = ('payment_id', 'patient__first_name', 'patient__last_name', 'reference_number')
    readonly_fields = ('payment_id', 'payment_date', 'created_at')

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'patient', 'insurance_provider', 'claim_amount', 'approved_amount', 'status')
    list_filter = ('status', 'insurance_provider', 'submission_date')
    search_fields = ('claim_number', 'patient__first_name', 'patient__last_name', 'policy_number')
    readonly_fields = ('claim_number', 'submission_date', 'created_at')

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'patient', 'total_amount', 'monthly_payment', 'payments_made', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('plan_id', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('plan_id', 'created_at')

@admin.register(BillingAuditLog)
class BillingAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'performed_by', 'invoice', 'payment', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('details', 'invoice__invoice_number', 'payment__payment_id', 'performed_by__username')
    readonly_fields = ('action', 'performed_by', 'timestamp', 'invoice', 'payment', 'details')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class GroupInvoiceItemInline(admin.TabularInline):
    model = GroupInvoiceItem
    extra = 1
    fields = ['patient', 'service_date', 'description', 'quantity', 'unit_price', 'total_amount']
    readonly_fields = ['total_amount']
    autocomplete_fields = ['patient', 'service', 'appointment', 'lab_test_request']


class GroupPaymentInline(admin.TabularInline):
    model = GroupPayment
    extra = 0
    fields = ['payment_id', 'amount', 'payment_method', 'payment_date', 'status', 'reference_number']
    readonly_fields = ['payment_id', 'payment_date']


@admin.register(GroupInvoice)
class GroupInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'patient_group', 'invoice_type', 'period_display', 
        'total_amount', 'balance_due_display', 'status', 'issue_date', 'due_date'
    ]
    list_filter = ['status', 'invoice_type', 'patient_group', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'patient_group__name', 'billing_contact_name', 'billing_contact_email']
    readonly_fields = [
        'invoice_number', 'subtotal', 'tax_amount', 'total_amount', 
        'patient_count_display', 'service_count_display', 'total_paid_display', 
        'balance_due_display', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'issue_date'
    inlines = [GroupInvoiceItemInline, GroupPaymentInline]
    actions = ['generate_period_invoice', 'mark_as_sent', 'mark_as_paid', 'export_to_pdf']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'patient_group', 'invoice_type', 'status')
        }),
        ('Period (for Auto-Generated Invoices)', {
            'fields': ('period_start', 'period_end'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Billing Contact', {
            'fields': ('billing_contact_name', 'billing_contact_email', 'billing_contact_phone', 'billing_address')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Payment Summary', {
            'fields': ('total_paid_display', 'balance_due_display', 'patient_count_display', 'service_count_display')
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms_and_conditions')
        }),
        ('PDF URLs', {
            'fields': ('invoice_pdf_url', 'gdrive_pdf_url'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def period_display(self, obj):
        if obj.period_start and obj.period_end:
            return f"{obj.period_start:%d/%m/%Y} - {obj.period_end:%d/%m/%Y}"
        return "—"
    period_display.short_description = "Period"
    
    def balance_due_display(self, obj):
        balance = obj.get_balance_due()
        balance_display = f"{balance:,.2f}"
        if balance > 0:
            return format_html('<span style="color: red; font-weight: bold;">UGX {}</span>', balance_display)
        return format_html('<span style="color: green;">UGX 0.00</span>')
    balance_due_display.short_description = "Balance Due"
    
    def total_paid_display(self, obj):
        total_paid = obj.get_total_paid()
        return f"UGX {total_paid:,.2f}"
    total_paid_display.short_description = "Total Paid"
    
    def patient_count_display(self, obj):
        return obj.get_patient_count()
    patient_count_display.short_description = "Patients"
    
    def service_count_display(self, obj):
        return obj.get_service_count()
    service_count_display.short_description = "Services"
    
    def generate_period_invoice(self, request, queryset):
        # This action is placeholder - actual generation happens in a custom view
        self.message_user(request, "Use the 'Generate Group Invoice' button to create period-based invoices.")
    generate_period_invoice.short_description = "Generate invoice for period"
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} invoice(s) marked as sent.')
    mark_as_sent.short_description = 'Mark as Sent'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} invoice(s) marked as paid.')
    mark_as_paid.short_description = 'Mark as Paid'
    
    def export_to_pdf(self, request, queryset):
        self.message_user(request, "PDF export feature coming soon.")
    export_to_pdf.short_description = 'Export to PDF'
    
    def save_model(self, request, obj, form, change):
        if not change:
            # Generate invoice number for new invoices
            from django.utils import timezone
            last_invoice = GroupInvoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.invoice_number.startswith('GRP-'):
                try:
                    last_num = int(last_invoice.invoice_number.split('-')[1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            obj.invoice_number = f"GRP-{new_num:05d}"
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GroupInvoiceItem)
class GroupInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['group_invoice', 'patient', 'service_date', 'description', 'quantity', 'unit_price', 'total_amount']
    list_filter = ['service_date', 'group_invoice__patient_group']
    search_fields = ['description', 'patient__first_name', 'patient__last_name', 'group_invoice__invoice_number']
    readonly_fields = ['total_amount']
    raw_id_fields = ['group_invoice', 'patient', 'appointment', 'lab_test_request']
    autocomplete_fields = ['service']
    date_hierarchy = 'service_date'


@admin.register(GroupPayment)
class GroupPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'group_invoice', 'amount', 'payment_method', 'payment_date', 'status', 'reference_number']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['payment_id', 'reference_number', 'group_invoice__invoice_number', 'group_invoice__patient_group__name']
    readonly_fields = ['payment_id', 'payment_date', 'created_at']
    raw_id_fields = ['group_invoice']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'group_invoice', 'amount', 'payment_method', 'status')
        }),
        ('Payment Details', {
            'fields': ('reference_number', 'notes', 'payment_date')
        }),
        ('PDF URLs', {
            'fields': ('receipt_pdf_url', 'gdrive_pdf_url'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('processed_by', 'created_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            # Generate payment ID for new payments
            last_payment = GroupPayment.objects.order_by('-id').first()
            if last_payment and last_payment.payment_id.startswith('GRPPAY-'):
                try:
                    last_num = int(last_payment.payment_id.split('-')[1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            obj.payment_id = f"GRPPAY-{new_num:05d}"
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)
