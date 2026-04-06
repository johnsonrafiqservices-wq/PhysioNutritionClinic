from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from decimal import Decimal
from .models import Batch, Medication, StockAlert

class InventoryManager:
    @staticmethod
    def check_low_stock_medications():
        """Check for medications that are below their reorder level."""
        low_stock_items = []
        for medication in Medication.objects.all():
            current_stock = medication.get_current_stock()
            if current_stock <= medication.reorder_level:
                low_stock_items.append({
                    'medication': medication,
                    'current_stock': current_stock,
                    'reorder_level': medication.reorder_level
                })
                # Create or update stock alert
                StockAlert.objects.update_or_create(
                    medication=medication,
                    defaults={
                        'current_stock': current_stock,
                        'reorder_level': medication.reorder_level,
                        'status': 'pending'
                    }
                )
        return low_stock_items

    @staticmethod
    def get_expiring_batches(days=30):
        """Get batches that will expire within the specified number of days."""
        threshold_date = timezone.now().date() + timezone.timedelta(days=days)
        return Batch.objects.filter(
            expiry_date__lte=threshold_date,
            expiry_date__gte=timezone.now().date(),
            quantity_remaining__gt=0
        ).order_by('expiry_date')

    @staticmethod
    def get_batch_value():
        """Calculate the total value of inventory."""
        return Batch.objects.annotate(
            batch_value=ExpressionWrapper(
                F('quantity_remaining') * F('unit_price'),
                output_field=DecimalField()
            )
        ).aggregate(
            total_value=Sum('batch_value')
        )['total_value'] or Decimal('0.00')

    @staticmethod
    def get_stock_movement_report(medication, start_date, end_date):
        """Generate stock movement report for a specific medication."""
        batches = Batch.objects.filter(
            medication=medication,
            created_at__range=[start_date, end_date]
        )
        
        stock_movement = []
        total_received = 0
        total_dispensed = 0
        
        for batch in batches:
            # Calculate received quantity from stock movements
            received = batch.movements.filter(movement_type='in').aggregate(
                total=Sum('quantity'))['total'] or 0
            # Calculate dispensed quantity from stock movements
            dispensed = batch.movements.filter(movement_type__in=['out', 'adjustment']).aggregate(
                total=Sum('quantity'))['total'] or 0
            
            stock_movement.append({
                'batch_number': batch.batch_number,
                'date': batch.created_at,
                'received': received,
                'dispensed': dispensed,
                'balance': batch.quantity_remaining,
                'expiry_date': batch.expiry_date
            })
            
            total_received += received
            total_dispensed += dispensed
        
        return {
            'movements': stock_movement,
            'summary': {
                'total_received': total_received,
                'total_dispensed': total_dispensed,
                'current_stock': medication.get_current_stock()
            }
        }

    @staticmethod
    def record_stock_adjustment(batch, quantity, reason, adjusted_by):
        """Record a stock adjustment with proper tracking."""
        from .models import StockAdjustment
        
        previous_quantity = batch.quantity_remaining
        batch.quantity_remaining = max(0, batch.quantity_remaining + quantity)
        batch.save()
        
        StockAdjustment.objects.create(
            batch=batch,
            previous_quantity=previous_quantity,
            adjusted_quantity=quantity,
            new_quantity=batch.current_quantity,
            reason=reason,
            adjusted_by=adjusted_by
        )
        
        # Check if need to create stock alert
        if batch.current_quantity <= batch.medication.reorder_level:
            StockAlert.objects.get_or_create(
                medication=batch.medication,
                defaults={
                    'current_stock': batch.medication.get_current_stock(),
                    'reorder_level': batch.medication.reorder_level,
                    'status': 'pending'
                }
            )