from django.contrib import admin
from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'status', 'subscription_plan', 'subscription_expires', 'created_at')
    list_filter = ('status', 'subscription_plan', 'country')
    search_fields = ('name', 'subdomain', 'email', 'contact_person')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
