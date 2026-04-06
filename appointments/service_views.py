from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from accounts.permissions import admin_or_manager_required
from .models import Service


@login_required
@admin_or_manager_required
def service_list(request):
    """List all services"""
    services = Service.objects.all().order_by('category', 'name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    if category_filter:
        services = services.filter(category=category_filter)
    
    if status_filter == 'active':
        services = services.filter(is_active=True)
    elif status_filter == 'inactive':
        services = services.filter(is_active=False)
    
    # Get unique categories for filter dropdown
    categories = Service.objects.values_list('category', flat=True).distinct().order_by('category')
    
    context = {
        'services': services,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }
    return render(request, 'appointments/service_list.html', context)


@login_required
@admin_or_manager_required
def service_create(request):
    """Create a new service via AJAX"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        base_price = request.POST.get('base_price', '').strip()
        duration = request.POST.get('duration', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Service name is required.'
            }, status=400)
        
        if not category:
            return JsonResponse({
                'success': False,
                'message': 'Category is required.'
            }, status=400)
        
        if not base_price:
            return JsonResponse({
                'success': False,
                'message': 'Base price is required.'
            }, status=400)
        
        try:
            base_price = float(base_price)
            if base_price < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Base price cannot be negative.'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid price format.'
            }, status=400)
        
        # Duration validation
        if duration:
            try:
                duration = int(duration)
                if duration < 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'Duration cannot be negative.'
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid duration format.'
                }, status=400)
        else:
            duration = None
        
        # Check if service with same name exists
        if Service.objects.filter(name__iexact=name).exists():
            return JsonResponse({
                'success': False,
                'message': f'A service with the name "{name}" already exists.'
            }, status=400)
        
        service = Service.objects.create(
            name=name,
            category=category,
            description=description,
            base_price=base_price,
            duration_minutes=duration,
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Service "{service.name}" created successfully!',
            'service': {
                'id': service.id,
                'name': service.name,
                'category': service.category,
                'description': service.description,
                'base_price': float(service.base_price),
                'duration_minutes': service.duration_minutes,
                'is_active': service.is_active,
            }
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def service_update(request, service_id):
    """Update an existing service via AJAX"""
    service = get_object_or_404(Service, pk=service_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        base_price = request.POST.get('base_price', '').strip()
        duration = request.POST.get('duration', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Service name is required.'
            }, status=400)
        
        if not category:
            return JsonResponse({
                'success': False,
                'message': 'Category is required.'
            }, status=400)
        
        if not base_price:
            return JsonResponse({
                'success': False,
                'message': 'Base price is required.'
            }, status=400)
        
        try:
            base_price = float(base_price)
            if base_price < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Base price cannot be negative.'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid price format.'
            }, status=400)
        
        # Duration validation
        if duration:
            try:
                duration = int(duration)
                if duration < 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'Duration cannot be negative.'
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid duration format.'
                }, status=400)
        else:
            duration = None
        
        # Check if another service with same name exists
        if Service.objects.filter(name__iexact=name).exclude(pk=service_id).exists():
            return JsonResponse({
                'success': False,
                'message': f'A service with the name "{name}" already exists.'
            }, status=400)
        
        service.name = name
        service.category = category
        service.description = description
        service.base_price = base_price
        service.duration_minutes = duration
        service.is_active = is_active
        service.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Service "{service.name}" updated successfully!',
            'service': {
                'id': service.id,
                'name': service.name,
                'category': service.category,
                'description': service.description,
                'base_price': float(service.base_price),
                'duration_minutes': service.duration_minutes,
                'is_active': service.is_active,
            }
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def service_delete(request, service_id):
    """Delete a service via AJAX"""
    service = get_object_or_404(Service, pk=service_id)
    
    if request.method == 'POST':
        # Check if service has appointments
        appointment_count = service.appointments.count() if hasattr(service, 'appointments') else 0
        
        if appointment_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete this service. It has {appointment_count} appointment(s) associated with it. Consider deactivating it instead.'
            }, status=400)
        
        service_name = service.name
        service.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Service "{service_name}" deleted successfully!'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
@admin_or_manager_required
def service_get(request, service_id):
    """Get service details via AJAX"""
    service = get_object_or_404(Service, pk=service_id)
    
    return JsonResponse({
        'success': True,
        'service': {
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'description': service.description,
            'base_price': float(service.base_price),
            'duration_minutes': service.duration_minutes,
            'is_active': service.is_active,
        }
    })
