from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from accounts.permissions import admin_or_manager_required
from .models import LabTest, LabTestPriceGroup, TestCategory
from patients.models import PatientGroup


@login_required
@admin_or_manager_required
def lab_test_price_group_list(request):
    """List all lab tests with their group prices"""
    # Get all lab tests with their group prices
    lab_tests = LabTest.objects.filter(is_active=True).prefetch_related('group_prices__patient_group').order_by('category', 'name')
    patient_groups = PatientGroup.objects.filter(is_active=True).order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    if search_query:
        lab_tests = lab_tests.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if category_filter:
        try:
            category_obj = TestCategory.objects.get(code=category_filter)
            lab_tests = lab_tests.filter(category=category_obj)
        except TestCategory.DoesNotExist:
            lab_tests = lab_tests.none()
    
    # Get unique categories for filter dropdown
    categories = TestCategory.objects.filter(is_active=True)
    
    context = {
        'lab_tests': lab_tests,
        'patient_groups': patient_groups,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'laboratory/lab_test_price_group_list.html', context)


@login_required
@admin_or_manager_required
def lab_test_price_group_set(request):
    """Set or update a lab test price for a specific group via AJAX"""
    if request.method == 'POST':
        lab_test_id = request.POST.get('lab_test_id')
        group_id = request.POST.get('group_id')
        price = request.POST.get('price')
        
        if not all([lab_test_id, group_id, price]):
            return JsonResponse({
                'success': False,
                'message': 'Lab test, group, and price are required.'
            }, status=400)
        
        try:
            lab_test = LabTest.objects.get(pk=lab_test_id)
            group = PatientGroup.objects.get(pk=group_id)
            price = float(price)
            
            if price < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Price cannot be negative.'
                }, status=400)
            
            # Create or update the price
            price_group, created = LabTestPriceGroup.objects.update_or_create(
                lab_test=lab_test,
                patient_group=group,
                defaults={'price': price}
            )
            
            action = 'set' if created else 'updated'
            return JsonResponse({
                'success': True,
                'message': f'Price {action} successfully for {lab_test.name} - {group.name}',
                'price_group': {
                    'id': price_group.id,
                    'lab_test_id': lab_test.id,
                    'group_id': group.id,
                    'price': float(price_group.price),
                }
            })
            
        except LabTest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Lab test not found.'
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
def lab_test_price_group_delete(request):
    """Delete a lab test price group via AJAX"""
    if request.method == 'POST':
        lab_test_id = request.POST.get('lab_test_id')
        group_id = request.POST.get('group_id')
        
        if not all([lab_test_id, group_id]):
            return JsonResponse({
                'success': False,
                'message': 'Lab test and group are required.'
            }, status=400)
        
        try:
            price_group = LabTestPriceGroup.objects.get(
                lab_test_id=lab_test_id,
                patient_group_id=group_id
            )
            lab_test_name = price_group.lab_test.name
            group_name = price_group.patient_group.name
            price_group.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Custom price removed for {lab_test_name} - {group_name}. Default price will be used.'
            })
            
        except LabTestPriceGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Price group not found.'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
