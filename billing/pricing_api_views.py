from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from appointments.models import Service
from laboratory.models import LabTest, LabTestPriceGroup
from patients.models import Patient
from .models import ServicePriceGroup


@login_required
@require_http_methods(["GET"])
def get_service_price_for_patient(request):
    """
    Get the appropriate service price for a patient based on their group.
    Returns service details including group-adjusted price.
    """
    service_id = request.GET.get('service_id')
    patient_id = request.GET.get('patient_id')
    
    if not service_id:
        return JsonResponse({'error': 'Service ID is required'}, status=400)
    
    try:
        service = Service.objects.get(pk=service_id, is_active=True)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)
    
    # Get base price
    price = float(service.base_price)
    price_type = 'default'
    group_name = None
    
    # If patient is provided, check for group pricing
    if patient_id:
        try:
            patient = Patient.objects.get(pk=patient_id)
            if patient.patient_group:
                # Get group-specific price
                group_price = ServicePriceGroup.get_price_for_patient(service, patient)
                price = float(group_price)
                if abs(price - float(service.base_price)) > 0.01:
                    price_type = 'group'
                    group_name = patient.patient_group.name
        except Patient.DoesNotExist:
            pass
    
    return JsonResponse({
        'success': True,
        'service': {
            'id': service.id,
            'name': service.name,
            'description': service.description or '',
            'category': service.get_category_display(),
            'base_price': float(service.base_price),
            'price': price,
            'price_type': price_type,
            'group_name': group_name,
        }
    })


@login_required
@require_http_methods(["GET"])
def get_lab_test_price_for_patient(request):
    """
    Get the appropriate lab test price for a patient based on their group.
    Returns lab test details including group-adjusted price.
    """
    lab_test_id = request.GET.get('lab_test_id')
    patient_id = request.GET.get('patient_id')
    
    if not lab_test_id:
        return JsonResponse({'error': 'Lab test ID is required'}, status=400)
    
    try:
        lab_test = LabTest.objects.get(pk=lab_test_id, is_active=True)
    except LabTest.DoesNotExist:
        return JsonResponse({'error': 'Lab test not found'}, status=404)
    
    # Get base price
    price = float(lab_test.price)
    price_type = 'default'
    group_name = None
    
    # If patient is provided, check for group pricing
    if patient_id:
        try:
            patient = Patient.objects.get(pk=patient_id)
            if patient.patient_group:
                # Get group-specific price
                group_price = LabTestPriceGroup.get_price_for_patient(lab_test, patient)
                price = float(group_price)
                if abs(price - float(lab_test.price)) > 0.01:
                    price_type = 'group'
                    group_name = patient.patient_group.name
        except Patient.DoesNotExist:
            pass
    
    return JsonResponse({
        'success': True,
        'lab_test': {
            'id': lab_test.id,
            'name': lab_test.name,
            'code': lab_test.code,
            'category': lab_test.get_category_display(),
            'base_price': float(lab_test.price),
            'price': price,
            'currency': lab_test.currency,
            'price_type': price_type,
            'group_name': group_name,
        }
    })
