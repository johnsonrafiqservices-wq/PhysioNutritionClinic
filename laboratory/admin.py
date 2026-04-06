from django.contrib import admin
from django.utils.html import format_html
from .models import (
    LabTest, LabTestRequest, LabTestResult, LabTestPriceGroup,
    TestCategory, ParameterCategory, TestParameter, TestProfile, TestProfileParameter, ParameterResult
)


@admin.register(LabTestPriceGroup)
class LabTestPriceGroupAdmin(admin.ModelAdmin):
    list_display = ('lab_test', 'patient_group', 'price', 'price_difference')
    list_editable = ('price',)
    list_filter = ('patient_group', 'lab_test__category')
    search_fields = ('lab_test__name', 'patient_group__name')
    autocomplete_fields = ['lab_test', 'patient_group']
    
    def price_difference(self, obj):
        diff = obj.price - obj.lab_test.price
        if diff > 0:
            return format_html('<span style="color: green;">+{}</span>', diff)
        elif diff < 0:
            return format_html('<span style="color: red;">{}</span>', diff)
        return '0'
    price_difference.short_description = 'Diff from Base'

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'price', 'currency', 'sample_type', 'duration_hours', 'is_active', 'created_at']
    list_editable = ['category', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    list_per_page = 50
    date_hierarchy = 'created_at'
    actions = ['activate_tests', 'deactivate_tests', 'duplicate_tests']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'category', 'description', 'is_active')
        }),
        ('Test Configuration', {
            'fields': ('sample_type', 'duration_hours', 'normal_range')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Profile Link', {
            'fields': ('profile',),
            'classes': ('collapse',)
        }),
    )
    
    def activate_tests(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} test(s) activated successfully.')
    activate_tests.short_description = 'Activate selected tests'
    
    def deactivate_tests(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} test(s) deactivated successfully.')
    deactivate_tests.short_description = 'Deactivate selected tests'
    
    def duplicate_tests(self, request, queryset):
        for test in queryset:
            test.pk = None
            test.code = f"{test.code}_COPY"
            test.name = f"{test.name} (Copy)"
            test.save()
        self.message_user(request, f'{queryset.count()} test(s) duplicated successfully.')
    duplicate_tests.short_description = 'Duplicate selected tests'
    
@admin.register(LabTestRequest)
class LabTestRequestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test', 'status', 'priority', 'requested_by', 'date_requested', 'sample_collected_at', 'has_result']
    list_editable = ['status', 'priority']
    list_filter = ['status', 'priority', 'date_requested', 'test__category']
    search_fields = ['patient__first_name', 'patient__last_name', 'test__name', 'sample_id', 'reason_for_test']
    raw_id_fields = ['patient']
    ordering = ['-date_requested']
    date_hierarchy = 'date_requested'
    actions = ['mark_sample_collected', 'mark_in_progress', 'mark_completed', 'cancel_requests']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Test Information', {
            'fields': ('patient', 'test', 'priority', 'status')
        }),
        ('Test Details', {
            'fields': ('reason_for_test', 'samples_required', 'clinical_notes')
        }),
        ('Sample Information', {
            'fields': ('sample_id', 'sample_collected_at')
        }),
        ('PDF URLs', {
            'fields': ('certificate_pdf_url', 'certificate_gdrive_url', 'report_pdf_url', 'report_gdrive_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('requested_by', 'date_requested', 'created_at', 'updated_at')
        }),
    )
    
    def has_result(self, obj):
        return hasattr(obj, 'result') and obj.result is not None
    has_result.boolean = True
    has_result.short_description = 'Has Result'
    
    def mark_sample_collected(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='requested').update(status='sample_collected', sample_collected_at=timezone.now())
        self.message_user(request, f'{updated} request(s) marked as sample collected.')
    mark_sample_collected.short_description = 'Mark as Sample Collected'
    
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} request(s) marked as in progress.')
    mark_in_progress.short_description = 'Mark as In Progress'
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} request(s) marked as completed.')
    mark_completed.short_description = 'Mark as Completed'
    
    def cancel_requests(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} request(s) cancelled.')
    cancel_requests.short_description = 'Cancel selected requests'


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'lab_test_count', 'profile_count', 'display_order', 'is_active', 'created_at']
    list_editable = ['display_order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['display_order', 'name']
    actions = ['activate_categories', 'deactivate_categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Display Settings', {
            'fields': ('display_order',)
        }),
    )
    
    def lab_test_count(self, obj):
        return obj.lab_tests.count()
    lab_test_count.short_description = "Lab Tests"
    
    def profile_count(self, obj):
        return obj.test_profiles.count()
    profile_count.short_description = "Test Profiles"
    
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categor(ies) activated successfully.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categor(ies) deactivated successfully.')
    deactivate_categories.short_description = 'Deactivate selected categories'


class TestParameterInline(admin.TabularInline):
    model = TestParameter
    extra = 0
    fields = ['name', 'code', 'unit', 'result_type', 'flag_criteria', 'is_active']
    readonly_fields = ['created_at']
    ordering = ['display_order', 'name']


@admin.register(ParameterCategory)
class ParameterCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parameter_count', 'display_order', 'is_active', 'created_at']
    list_editable = ['display_order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['display_order', 'name']
    actions = ['activate_categories', 'deactivate_categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Display Settings', {
            'fields': ('display_order',)
        }),
    )
    
    def parameter_count(self, obj):
        return obj.parameters.count()
    parameter_count.short_description = "Parameters"
    
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categor(ies) activated successfully.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categor(ies) deactivated successfully.')
    deactivate_categories.short_description = 'Deactivate selected categories'
    
    inlines = [TestParameterInline]


class ParameterResultInline(admin.TabularInline):
    model = ParameterResult
    extra = 0
    fields = ['parameter', 'result_value', 'flag', 'notes']
    readonly_fields = ['created_at']


@admin.register(LabTestResult)
class LabTestResultAdmin(admin.ModelAdmin):
    list_display = ['request', 'result_value', 'is_abnormal', 'verified', 'verified_by', 'reported_by', 'date_reported', 'parameter_count']
    list_editable = ['verified']
    list_filter = ['is_abnormal', 'verified', 'date_reported', 'request__test__category']
    search_fields = ['request__patient__first_name', 'request__patient__last_name', 'request__test__name']
    ordering = ['-date_reported']
    raw_id_fields = ['request', 'reported_by', 'verified_by']
    readonly_fields = ['date_reported']
    date_hierarchy = 'date_reported'
    actions = ['verify_results', 'unverify_results']
    inlines = [ParameterResultInline]
    
    fieldsets = (
        ('Result Information', {
            'fields': ('request', 'result_value', 'result_unit', 'is_abnormal')
        }),
        ('Interpretation', {
            'fields': ('interpretation', 'remarks')
        }),
        ('Verification', {
            'fields': ('verified', 'verified_by', 'verified_at')
        }),
        ('Metadata', {
            'fields': ('reported_by', 'date_reported')
        }),
    )
    
    def parameter_count(self, obj):
        return obj.parameter_results.count()
    parameter_count.short_description = "Parameters"
    
    def verify_results(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(verified=True, verified_by=request.user, verified_at=timezone.now())
        self.message_user(request, f'{updated} result(s) verified successfully.')
    verify_results.short_description = 'Verify selected results'
    
    def unverify_results(self, request, queryset):
        updated = queryset.update(verified=False, verified_by=None, verified_at=None)
        self.message_user(request, f'{updated} result(s) unverified.')
    unverify_results.short_description = 'Unverify selected results'


@admin.register(TestParameter)
class TestParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'result_type', 'unit', 'reference_range_display', 'display_order', 'is_active']
    list_editable = ['category', 'result_type', 'unit', 'display_order', 'is_active']
    list_filter = ['category', 'result_type', 'flag_criteria', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['category', 'display_order', 'name']
    list_per_page = 50
    actions = ['activate_parameters', 'deactivate_parameters', 'duplicate_parameters']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'category', 'is_active')
        }),
        ('Result Configuration', {
            'fields': ('result_type', 'unit', 'display_order')
        }),
        ('Reference Range', {
            'fields': ('reference_range_min', 'reference_range_max', 'reference_range_text')
        }),
        ('Flagging Criteria', {
            'fields': ('flag_criteria', 'critical_low', 'critical_high', 'custom_options')
        }),
    )
    
    def reference_range_display(self, obj):
        if obj.reference_range_text:
            return obj.reference_range_text
        elif obj.reference_range_min is not None and obj.reference_range_max is not None:
            return f"{obj.reference_range_min} - {obj.reference_range_max}"
        elif obj.reference_range_min is not None:
            return f"≥ {obj.reference_range_min}"
        elif obj.reference_range_max is not None:
            return f"≤ {obj.reference_range_max}"
        return "Not set"
    reference_range_display.short_description = "Reference Range"
    
    def activate_parameters(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} parameter(s) activated successfully.')
    activate_parameters.short_description = 'Activate selected parameters'
    
    def deactivate_parameters(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} parameter(s) deactivated successfully.')
    deactivate_parameters.short_description = 'Deactivate selected parameters'
    
    def duplicate_parameters(self, request, queryset):
        for param in queryset:
            param.pk = None
            param.code = f"{param.code}_COPY"
            param.name = f"{param.name} (Copy)"
            param.save()
        self.message_user(request, f'{queryset.count()} parameter(s) duplicated successfully.')
    duplicate_parameters.short_description = 'Duplicate selected parameters'


class TestProfileParameterInline(admin.TabularInline):
    model = TestProfileParameter
    extra = 1
    fields = ['parameter', 'display_order']
    raw_id_fields = ['parameter']
    ordering = ['display_order']


@admin.register(TestProfile)
class TestProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'parameter_count', 'price', 'currency', 'is_active', 'created_at']
    list_editable = ['category', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    date_hierarchy = 'created_at'
    actions = ['activate_profiles', 'deactivate_profiles', 'duplicate_profiles']
    inlines = [TestProfileParameterInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'category', 'is_active')
        }),
        ('Test Details', {
            'fields': ('sample_type', 'duration_hours')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
    )
    
    def parameter_count(self, obj):
        return obj.parameters.count()
    parameter_count.short_description = "Parameters"
    
    def activate_profiles(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} profile(s) activated successfully.')
    activate_profiles.short_description = 'Activate selected profiles'
    
    def deactivate_profiles(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} profile(s) deactivated successfully.')
    deactivate_profiles.short_description = 'Deactivate selected profiles'
    
    def duplicate_profiles(self, request, queryset):
        for profile in queryset:
            old_params = list(profile.testprofileparameter_set.all())
            profile.pk = None
            profile.code = f"{profile.code}_COPY"
            profile.name = f"{profile.name} (Copy)"
            profile.save()
            for param_link in old_params:
                param_link.pk = None
                param_link.profile = profile
                param_link.save()
        self.message_user(request, f'{queryset.count()} profile(s) duplicated successfully.')
    duplicate_profiles.short_description = 'Duplicate selected profiles'


@admin.register(TestProfileParameter)
class TestProfileParameterAdmin(admin.ModelAdmin):
    list_display = ['profile', 'parameter', 'display_order']
    list_filter = ['profile__category', 'parameter__category']
    search_fields = ['profile__name', 'parameter__name', 'parameter__code']
    ordering = ['profile', 'display_order']
    raw_id_fields = ['profile', 'parameter']


@admin.register(ParameterResult)
class ParameterResultAdmin(admin.ModelAdmin):
    list_display = ['test_result', 'parameter', 'result_value', 'flag_display', 'notes', 'created_at']
    list_filter = ['flag', 'parameter__category', 'created_at']
    search_fields = [
        'test_result__request__patient__first_name',
        'test_result__request__patient__last_name',
        'parameter__name',
        'result_value'
    ]
    ordering = ['-created_at']
    raw_id_fields = ['test_result', 'parameter']
    
    fieldsets = (
        ('Result Information', {
            'fields': ('test_result', 'parameter', 'result_value')
        }),
        ('Flag Status', {
            'fields': ('flag',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def flag_display(self, obj):
        colors = {
            'normal': 'green',
            'low': 'orange',
            'high': 'orange',
            'critical_low': 'red',
            'critical_high': 'red',
            'abnormal': 'red',
            'pending': 'gray'
        }
        color = colors.get(obj.flag, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_flag_display() if hasattr(obj, 'get_flag_display') else obj.flag
        )
    flag_display.short_description = "Flag"
