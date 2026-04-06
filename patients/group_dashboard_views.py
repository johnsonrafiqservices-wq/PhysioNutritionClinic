from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from accounts.permissions import admin_or_manager_required
from .models import PatientGroup, Patient
from billing.models import ServicePriceGroup
from laboratory.models import LabTestPriceGroup, LabTest
from appointments.models import Service


@login_required
@admin_or_manager_required
def patient_group_dashboard(request, group_id=None):
    """
    Comprehensive dashboard for managing patient groups and their pricing
    """
    # Get all active patient groups
    patient_groups = PatientGroup.objects.filter(is_active=True).annotate(
        patient_count=Count('patients')
    ).order_by('name')
    
    # If a specific group is selected, get its details
    selected_group = None
    group_stats = None
    service_prices = []
    lab_test_prices = []
    
    if group_id:
        selected_group = get_object_or_404(PatientGroup, pk=group_id, is_active=True)
        
        # Get statistics for this group
        group_stats = {
            'total_patients': selected_group.patients.count(),
            'active_patients': selected_group.patients.filter(is_active=True).count(),
            'service_prices_set': ServicePriceGroup.objects.filter(patient_group=selected_group).count(),
            'lab_test_prices_set': LabTestPriceGroup.objects.filter(patient_group=selected_group).count(),
        }
        
        # Get all services with their prices for this group
        all_services = Service.objects.filter(is_active=True).order_by('category', 'name')
        service_prices = []
        for service in all_services:
            try:
                custom_price = ServicePriceGroup.objects.get(
                    service=service,
                    patient_group=selected_group
                )
                price = custom_price.price
                has_custom = True
            except ServicePriceGroup.DoesNotExist:
                price = service.base_price
                has_custom = False
            
            service_prices.append({
                'service': service,
                'price': price,
                'default_price': service.base_price,
                'has_custom': has_custom,
                'discount_percent': round(((float(service.base_price) - float(price)) / float(service.base_price) * 100), 1) if has_custom and service.base_price > 0 else 0
            })
        
        # Get all lab tests with their prices for this group
        all_lab_tests = LabTest.objects.filter(is_active=True).order_by('category', 'name')
        lab_test_prices = []
        for lab_test in all_lab_tests:
            try:
                custom_price = LabTestPriceGroup.objects.get(
                    lab_test=lab_test,
                    patient_group=selected_group
                )
                price = custom_price.price
                has_custom = True
            except LabTestPriceGroup.DoesNotExist:
                price = lab_test.price
                has_custom = False
            
            lab_test_prices.append({
                'lab_test': lab_test,
                'price': price,
                'default_price': lab_test.price,
                'has_custom': has_custom,
                'discount_percent': round(((float(lab_test.price) - float(price)) / float(lab_test.price) * 100), 1) if has_custom and lab_test.price > 0 else 0
            })
    
    # Get overall statistics
    overall_stats = {
        'total_groups': patient_groups.count(),
        'total_patients_in_groups': Patient.objects.filter(patient_group__isnull=False, is_active=True).count(),
        'total_services': Service.objects.filter(is_active=True).count(),
        'total_lab_tests': LabTest.objects.filter(is_active=True).count(),
    }
    
    # Get all lab tests for the modal
    lab_tests = LabTest.objects.filter(is_active=True).prefetch_related('group_prices').order_by('category', 'name')
    
    # Get all services for the modal
    services = Service.objects.filter(is_active=True).prefetch_related('group_prices').order_by('category', 'name')
    
    context = {
        'patient_groups': patient_groups,
        'selected_group': selected_group,
        'group_stats': group_stats,
        'service_prices': service_prices,
        'lab_test_prices': lab_test_prices,
        'overall_stats': overall_stats,
        'lab_tests': lab_tests,
        'services': services,
    }
    
    return render(request, 'patients/patient_group_dashboard.html', context)
