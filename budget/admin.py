from django.contrib import admin
from .models import ExpenseCategory, Budget, BudgetItem, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 1
    fields = ('category', 'allocated_amount', 'notes')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'period_type', 'start_date', 'end_date', 'total_amount', 'status', 'created_by')
    list_filter = ('status', 'period_type', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    inlines = [BudgetItemInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'allocated_amount', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('budget__name', 'category__name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'category', 'amount', 'expense_date', 'status', 'submitted_by', 'approved_by')
    list_filter = ('status', 'category', 'payment_method', 'expense_date')
    search_fields = ('description', 'vendor_name', 'reference_number')
    date_hierarchy = 'expense_date'
    readonly_fields = ('submitted_by', 'approved_by', 'approved_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'budget_item', 'description', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('expense_date', 'payment_method', 'reference_number', 'vendor_name')
        }),
        ('Additional Information', {
            'fields': ('notes', 'receipt_file')
        }),
        ('Approval', {
            'fields': ('status', 'submitted_by', 'approved_by', 'approved_date', 'rejection_reason')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)
