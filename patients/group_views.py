from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from accounts.permissions import admin_or_manager_required
from .models import Patient, PatientGroup
from billing.models import ServicePriceGroup, GroupInvoice, GroupPayment, Invoice
from appointments.models import Service
from laboratory.models import LabTest, LabTestPriceGroup, LabTestRequest


@login_required
@admin_or_manager_required
def patient_group_detail(request, group_id):
    """Single group detail management interface"""
    group = get_object_or_404(PatientGroup, pk=group_id)

    # Members
    members = group.patients.select_related('patient_group').order_by('first_name', 'last_name')
    total_patients = members.count()
    active_patients = members.filter(is_active=True).count()
    inactive_patients = total_patients - active_patients

    # Group invoices and payments
    group_invoices = GroupInvoice.objects.filter(
        patient_group=group
    ).order_by('-created_at')
    group_payments = GroupPayment.objects.filter(
        group_invoice__patient_group=group
    ).select_related('group_invoice', 'processed_by').order_by('-payment_date')

    # Group members are billed via GroupInvoice; hide individual invoices
    patient_ids = members.values_list('id', flat=True)
    invoices = Invoice.objects.none()

    # Services with group pricing
    from appointments.models import Service
    all_services = Service.objects.filter(is_active=True).order_by('category', 'name')
    services_with_prices = []
    for service in all_services:
        try:
            group_price = ServicePriceGroup.objects.get(service=service, patient_group=group)
            price_diff = group_price.price - service.base_price
            percentage_diff = (price_diff / service.base_price * 100) if service.base_price > 0 else 0
            services_with_prices.append({
                'id': service.id,
                'name': service.name,
                'category': service.category,
                'price': service.base_price,
                'group_price': group_price.price,
                'price_difference': price_diff,
                'percentage_difference': percentage_diff
            })
        except ServicePriceGroup.DoesNotExist:
            services_with_prices.append({
                'id': service.id,
                'name': service.name,
                'category': service.category,
                'price': service.base_price,
                'group_price': None,
                'price_difference': 0,
                'percentage_difference': 0
            })

    # Lab tests with group pricing
    all_lab_tests = LabTest.objects.filter(is_active=True).select_related('category').order_by('category', 'name')
    lab_tests_with_prices = []
    for lab_test in all_lab_tests:
        try:
            group_price = LabTestPriceGroup.objects.get(lab_test=lab_test, patient_group=group)
            price_diff = group_price.price - lab_test.price
            percentage_diff = (price_diff / lab_test.price * 100) if lab_test.price > 0 else 0
            lab_tests_with_prices.append({
                'id': lab_test.id,
                'name': lab_test.name,
                'category': lab_test.category,
                'price': lab_test.price,
                'group_price': group_price.price,
                'price_difference': price_diff,
                'percentage_difference': percentage_diff
            })
        except LabTestPriceGroup.DoesNotExist:
            lab_tests_with_prices.append({
                'id': lab_test.id,
                'name': lab_test.name,
                'category': lab_test.category,
                'price': lab_test.price,
                'group_price': None,
                'price_difference': 0,
                'percentage_difference': 0
            })

    # Test requests for group patients
    patient_ids = members.values_list('id', flat=True)
    test_requests = LabTestRequest.objects.filter(
        patient_id__in=patient_ids
    ).select_related('patient', 'requested_by', 'test', 'test__category').order_by('-created_at')
    
    # Group test requests by status
    completed_tests = test_requests.filter(status='completed')
    pending_tests = test_requests.filter(status__in=['scheduled', 'confirmed', 'in_progress'])

    context = {
        'group': group,
        'members': members,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'inactive_patients': inactive_patients,
        'group_invoices': group_invoices,
        'group_payments': group_payments,
        'invoices': invoices,
        'group_contact': None,
        'services_with_prices': services_with_prices,
        'all_services': all_services,
        'lab_tests_with_prices': lab_tests_with_prices,
        'all_lab_tests': all_lab_tests,
        'test_requests': test_requests,
        'completed_tests': completed_tests,
        'pending_tests': pending_tests,
    }
    return render(request, 'patients/patient_group_detail.html', context)


@login_required
@admin_or_manager_required
def patient_group_list(request):
    """List all patient groups with patient counts"""
    groups = PatientGroup.objects.annotate(
        patient_count=Count('patients')
    ).order_by('-is_active', 'name')
    
    # Get all active patients for assignment modal
    all_patients = Patient.objects.filter(is_active=True).select_related('patient_group').order_by('first_name', 'last_name')
    
    context = {
        'groups': groups,
        'all_patients': all_patients,
    }
    return render(request, 'patients/patient_group_list.html', context)


@login_required
@admin_or_manager_required
def patient_group_create(request):
    """Create a new patient group via AJAX"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Group name is required.'
            }, status=400)
        
        # Check if group with same name exists
        if PatientGroup.objects.filter(name__iexact=name).exists():
            return JsonResponse({
                'success': False,
                'message': f'A group with the name "{name}" already exists.'
            }, status=400)
        
        group = PatientGroup.objects.create(
            name=name,
            description=description,
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Patient group "{group.name}" created successfully!',
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'is_active': group.is_active,
            }
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def patient_group_update(request, group_id):
    """Update an existing patient group via AJAX"""
    group = get_object_or_404(PatientGroup, pk=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Group name is required.'
            }, status=400)
        
        # Check if another group with same name exists
        if PatientGroup.objects.filter(name__iexact=name).exclude(pk=group_id).exists():
            return JsonResponse({
                'success': False,
                'message': f'A group with the name "{name}" already exists.'
            }, status=400)
        
        group.name = name
        group.description = description
        group.is_active = is_active
        group.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Patient group "{group.name}" updated successfully!',
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'is_active': group.is_active,
            }
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def patient_group_delete(request, group_id):
    """Delete a patient group via AJAX"""
    group = get_object_or_404(PatientGroup, pk=group_id)
    
    if request.method == 'POST':
        # Check if group has patients
        patient_count = group.patients.count()
        if patient_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete this group. It has {patient_count} patient(s) assigned. Please reassign or remove patients first.'
            }, status=400)
        
        group_name = group.name
        group.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Patient group "{group_name}" deleted successfully!'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def patient_group_get(request, group_id):
    """Get patient group details via AJAX"""
    group = get_object_or_404(PatientGroup, pk=group_id)
    
    return JsonResponse({
        'success': True,
        'group': {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'is_active': group.is_active,
        }
    })


@login_required
@admin_or_manager_required
def service_price_group_list(request):
    """List all service price groups"""
    # Get all services with their group prices
    services = Service.objects.filter(is_active=True).prefetch_related('group_prices__patient_group').order_by('category', 'name')
    patient_groups = PatientGroup.objects.filter(is_active=True).order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    context = {
        'services': services,
        'patient_groups': patient_groups,
        'search_query': search_query,
    }
    return render(request, 'patients/service_price_group_list.html', context)


@login_required
@admin_or_manager_required
def service_price_group_set(request):
    """Set or update a service price for a specific group via AJAX"""
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        group_id = request.POST.get('group_id')
        price = request.POST.get('price')
        
        if not all([service_id, group_id, price]):
            return JsonResponse({
                'success': False,
                'message': 'Service, group, and price are required.'
            }, status=400)
        
        try:
            service = Service.objects.get(pk=service_id)
            group = PatientGroup.objects.get(pk=group_id)
            price = float(price)
            
            if price < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Price cannot be negative.'
                }, status=400)
            
            # Create or update the price
            price_group, created = ServicePriceGroup.objects.update_or_create(
                service=service,
                patient_group=group,
                defaults={'price': price}
            )
            
            action = 'set' if created else 'updated'
            return JsonResponse({
                'success': True,
                'message': f'Price {action} successfully for {service.name} - {group.name}',
                'price_group': {
                    'id': price_group.id,
                    'service_id': service.id,
                    'group_id': group.id,
                    'price': float(price_group.price),
                }
            })
            
        except Service.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Service not found.'
            }, status=404)
        except PatientGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Patient group not found.'
            }, status=404)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid price value.'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def service_price_group_delete(request):
    """Delete a service price group via AJAX"""
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        group_id = request.POST.get('group_id')
        
        if not all([service_id, group_id]):
            return JsonResponse({
                'success': False,
                'message': 'Service and group are required.'
            }, status=400)
        
        try:
            price_group = ServicePriceGroup.objects.get(
                service_id=service_id,
                patient_group_id=group_id
            )
            service_name = price_group.service.name
            group_name = price_group.patient_group.name
            price_group.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Custom price removed for {service_name} - {group_name}. Default price will be used.'
            })
            
        except ServicePriceGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Price group not found.'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def assign_patient_to_group(request):
    """Assign or unassign a patient to/from a group via AJAX"""
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        group_id = request.POST.get('group_id')
        
        if not patient_id:
            return JsonResponse({
                'success': False,
                'message': 'Patient ID is required.'
            }, status=400)
        
        try:
            patient = Patient.objects.get(pk=patient_id)
            
            if group_id:
                # Assign to group
                group = PatientGroup.objects.get(pk=group_id)
                patient.patient_group = group
                patient.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'{patient.get_full_name()} assigned to {group.name} successfully!'
                })
            else:
                # Unassign from group
                patient.patient_group = None
                patient.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'{patient.get_full_name()} removed from group successfully!'
                })
                
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Patient not found.'
            }, status=404)
        except PatientGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Patient group not found.'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def group_patients_list(request, group_id):
    """Get list of patients in a specific group via AJAX"""
    group = get_object_or_404(PatientGroup, pk=group_id)
    
    patients = group.patients.filter(is_active=True).values(
        'id', 'first_name', 'last_name', 'patient_id', 'phone'
    )
    
    patients_list = []
    for patient in patients:
        patients_list.append({
            'id': patient['id'],
            'full_name': f"{patient['first_name']} {patient['last_name']}",
            'patient_id': patient['patient_id'],
            'phone': patient['phone'] or ''
        })
    
    return JsonResponse({
        'success': True,
        'patients': patients_list,
        'group': {
            'id': group.id,
            'name': group.name
        }
    })
