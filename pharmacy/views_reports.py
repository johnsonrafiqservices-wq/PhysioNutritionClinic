"""
Pharmacy Reports and Analytics Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from .models import Medication, Batch, Prescription, StockMovement, PurchaseOrder, StockAlert


@login_required
def expiry_alerts(request):
    """View for managing medication expiry alerts."""
    today = timezone.now().date()
    
    # Batches expiring in next 30 days
    expiring_30_days = Batch.objects.filter(
        is_active=True,
        expiry_date__gt=today,
        expiry_date__lte=today + timedelta(days=30),
        quantity_remaining__gt=0
    ).select_related('medication', 'supplier').order_by('expiry_date')
    
    # Batches expiring in next 90 days
    expiring_90_days = Batch.objects.filter(
        is_active=True,
        expiry_date__gt=today + timedelta(days=30),
        expiry_date__lte=today + timedelta(days=90),
        quantity_remaining__gt=0
    ).select_related('medication', 'supplier').order_by('expiry_date')
    
    # Already expired batches
    expired_batches = Batch.objects.filter(
        is_active=True,
        expiry_date__lte=today,
        quantity_remaining__gt=0
    ).select_related('medication', 'supplier').order_by('expiry_date')
    
    context = {
        'title': 'Expiry Alerts',
        'expiring_30_days': expiring_30_days,
        'expiring_90_days': expiring_90_days,
        'expired_batches': expired_batches,
        'expiring_30_count': expiring_30_days.count(),
        'expiring_90_count': expiring_90_days.count(),
        'expired_count': expired_batches.count(),
    }
    return render(request, 'pharmacy/expiry_alerts.html', context)


@login_required
def low_stock_alerts(request):
    """View for managing low stock alerts."""
    # Get medications with low stock
    low_stock_medications = Medication.objects.filter(
        is_active=True
    ).annotate(
        total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
    ).filter(
        Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
    ).select_related('category')
    
    # Get or create stock alerts
    for med in low_stock_medications:
        StockAlert.objects.get_or_create(
            medication=med,
            status='pending',
            defaults={
                'current_stock': med.total_stock or 0,
                'reorder_level': med.reorder_level
            }
        )
    
    # Get all pending alerts
    pending_alerts = StockAlert.objects.filter(
        status='pending'
    ).select_related('medication')
    
    context = {
        'title': 'Low Stock Alerts',
        'pending_alerts': pending_alerts,
        'low_stock_medications': low_stock_medications,
    }
    return render(request, 'pharmacy/low_stock_alerts.html', context)


@login_required
def pharmacy_analytics(request):
    """Comprehensive pharmacy analytics dashboard."""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Stock statistics
    total_medications = Medication.objects.filter(is_active=True).count()
    total_batches = Batch.objects.filter(is_active=True).count()
    
    # Calculate total inventory value
    total_value = Batch.objects.filter(
        is_active=True,
        expiry_date__gt=today
    ).aggregate(
        total=ExpressionWrapper(
            Sum(F('quantity_remaining') * F('selling_price')),
            output_field=DecimalField()
        )
    )['total'] or 0
    
    # Prescription statistics
    total_prescriptions = Prescription.objects.count()
    pending_prescriptions = Prescription.objects.filter(status='pending').count()
    dispensed_last_30_days = Prescription.objects.filter(
        status='dispensed',
        dispensed_date__gte=thirty_days_ago
    ).count()
    
    # Stock movement statistics
    stock_in_30_days = StockMovement.objects.filter(
        movement_type='in',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    stock_out_30_days = StockMovement.objects.filter(
        movement_type='out',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Alert statistics
    low_stock_count = Medication.objects.filter(
        is_active=True
    ).annotate(
        total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
    ).filter(
        Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
    ).count()
    
    expiring_soon_count = Batch.objects.filter(
        is_active=True,
        expiry_date__gt=today,
        expiry_date__lte=today + timedelta(days=90),
        quantity_remaining__gt=0
    ).count()
    
    # Top medications by dispensing
    top_medications = Prescription.objects.filter(
        status='dispensed',
        dispensed_date__gte=thirty_days_ago
    ).values(
        'medication__name'
    ).annotate(
        total_dispensed=Sum('quantity')
    ).order_by('-total_dispensed')[:10]
    
    context = {
        'title': 'Pharmacy Analytics',
        'total_medications': total_medications,
        'total_batches': total_batches,
        'total_value': total_value,
        'total_prescriptions': total_prescriptions,
        'pending_prescriptions': pending_prescriptions,
        'dispensed_last_30_days': dispensed_last_30_days,
        'stock_in_30_days': stock_in_30_days,
        'stock_out_30_days': stock_out_30_days,
        'low_stock_count': low_stock_count,
        'expiring_soon_count': expiring_soon_count,
        'top_medications': top_medications,
    }
    return render(request, 'pharmacy/analytics.html', context)


@login_required
def purchase_order_list(request):
    """List all purchase orders."""
    status_filter = request.GET.get('status')
    
    purchase_orders = PurchaseOrder.objects.all().select_related('supplier', 'created_by')
    
    if status_filter:
        purchase_orders = purchase_orders.filter(status=status_filter)
    
    context = {
        'title': 'Purchase Orders',
        'purchase_orders': purchase_orders,
        'status_filter': status_filter,
    }
    return render(request, 'pharmacy/purchase_order_list.html', context)
