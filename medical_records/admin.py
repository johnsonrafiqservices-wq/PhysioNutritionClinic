from django.contrib import admin
from .models import MedicalRecord, Document

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'record_type', 'created_by', 'created_at')
    list_filter = ('record_type', 'created_at', 'created_by')
    search_fields = ('title', 'patient__first_name', 'patient__last_name', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at', 'uploaded_by')
    search_fields = ('title', 'patient__first_name', 'patient__last_name', 'description')
    readonly_fields = ('uploaded_at',)
