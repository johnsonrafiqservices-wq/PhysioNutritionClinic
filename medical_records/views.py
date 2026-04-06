from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import MedicalRecord, Document
from .forms import MedicalRecordForm, DocumentForm
from patients.models import Patient
from .decorators import medical_staff_required, can_view_medical_records

@login_required
def medical_record_list(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check if user can view medical records
    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)
    
    records = patient.medical_records.all()
    
    # Filter by record type
    record_type = request.GET.get('type')
    if record_type:
        records = records.filter(record_type=record_type)
    
    context = {
        'patient': patient,
        'records': records,
        'record_types': MedicalRecord.RECORD_TYPES,
        'selected_type': record_type,
        'can_edit': request.user.role in ['doctor', 'nutritionist', 'admin'],
    }
    return render(request, 'medical_records/record_list.html', context)

@medical_staff_required
def medical_record_create(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.created_by = request.user
            record.save()
            messages.success(request, 'Medical record created successfully!')
            return redirect('medical_records:record_list', patient_id=patient.patient_id)
    else:
        form = MedicalRecordForm()
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'medical_records/record_create.html', context)

@login_required
def medical_record_detail(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    
    # Check if user can view medical records
    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)
    
    context = {
        'record': record,
        'can_edit': request.user.role in ['doctor', 'nutritionist', 'admin'],
    }
    return render(request, 'medical_records/record_detail.html', context)

@login_required
def document_list(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    documents = patient.documents.all()
    
    # Filter by document type
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    context = {
        'patient': patient,
        'documents': documents,
        'document_types': Document.DOCUMENT_TYPES,
        'selected_type': doc_type,
    }
    return render(request, 'medical_records/document_list.html', context)

@medical_staff_required
def document_upload(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('medical_records:document_list', patient_id=patient.patient_id)
    else:
        form = DocumentForm()
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'medical_records/document_upload.html', context)
