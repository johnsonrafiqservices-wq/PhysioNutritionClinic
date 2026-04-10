from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib import messages
from django.db import transaction
from django.apps import apps
from .models import User
from .widgets import GroupedPermissionsWidget


class CustomUserChangeForm(UserChangeForm):
    role = forms.CharField(
        widget=forms.Select(attrs={'size': '15', 'style': 'width:100%;'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = User.ROLE_CHOICES
        self.fields['role'].widget.choices = User.ROLE_CHOICES
        if 'user_permissions' in self.fields:
            self.fields['user_permissions'].widget = GroupedPermissionsWidget()


class CustomUserCreationForm(UserCreationForm):
    role = forms.CharField(
        widget=forms.Select(attrs={'size': '15', 'style': 'width:100%;'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = User.ROLE_CHOICES
        self.fields['role'].widget.choices = User.ROLE_CHOICES

def wipe_all_clinic_data(modeladmin, request, queryset):
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can perform this action.")
        return

    app_labels = [
        'patients',
        'appointments',
        'billing',
        'pharmacy',
        'laboratory',
        'medical_records',
        'inventory',
        'reports',
        'staff_management',
        'budget',
    ]

    try:
        with transaction.atomic():
            for app_label in app_labels:
                app_config = apps.get_app_config(app_label)
                for model in app_config.get_models():
                    model.objects.all().delete()
        messages.success(request, "All clinic data for the selected apps has been deleted.")
    except Exception as exc:
        messages.error(request, f"Error while deleting clinic data: {exc}")


wipe_all_clinic_data.short_description = "WIPE ALL CLINIC DATA (SUPERUSER ONLY)"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active_employee', 'date_joined_clinic')
    list_filter = ('role', 'is_active_employee', 'date_joined_clinic', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee_id')
    ordering = ('username',)
    actions = [wipe_all_clinic_data]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Clinic Information', {
            'fields': ('role', 'phone', 'employee_id', 'department', 'is_active_employee', 'profile_picture')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Clinic Information', {
            'fields': ('role', 'phone', 'employee_id', 'department', 'is_active_employee')
        }),
    )
