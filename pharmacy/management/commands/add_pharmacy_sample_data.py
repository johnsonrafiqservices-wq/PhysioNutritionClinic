from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from pharmacy.models import Supplier, Category, Medication, Batch, StockMovement
from accounts.models import User

class Command(BaseCommand):
    help = 'Add sample pharmacy data including medications, batches, and sales'

    def handle(self, *args, **kwargs):
        # Get or create a user for the transactions
        user = User.objects.filter(is_staff=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No staff user found. Please create a user first.'))
            return
        
        # Create or get supplier
        supplier, created = Supplier.objects.get_or_create(
            name='PharmaCare Suppliers Ltd',
            defaults={
                'contact_person': 'John Mukasa',
                'email': 'info@pharmacare.ug',
                'phone': '+256 700 123456',
                'address': 'Kampala, Uganda',
                'is_active': True
            }
        )
        
        # Create or get category
        category, created = Category.objects.get_or_create(
            name='Pain Relief',
            defaults={'description': 'Pain relief and anti-inflammatory medications'}
        )
        
        # Create or get medication
        medication, created = Medication.objects.get_or_create(
            name='Paracetamol',
            generic_name='Acetaminophen',
            defaults={
                'category': category,
                'strength': '500mg',
                'form': 'tablet',
                'reorder_level': 100,
                'unit_price': 1000,  # UGX 1000 per tablet
                'unit_of_measure': 'Tablet',
                'manufacturer': 'Quality Pharma Ltd',
                'storage_instructions': 'Store in a cool, dry place',
                'requires_prescription': False,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created medication: {medication.name}'))
        
        # Create or get a batch
        batch, batch_created = Batch.objects.get_or_create(
            batch_number='PARA2024001',
            defaults={
                'medication': medication,
                'supplier': supplier,
                'quantity_remaining': 500,
                'cost_price': 500,  # Cost price UGX 500
                'selling_price': 1000,  # Selling price UGX 1000
                'manufacturing_date': datetime.now().date() - timedelta(days=180),
                'expiry_date': datetime.now().date() + timedelta(days=365),
                'received_by': user,
                'invoice_number': 'INV-2024-001',
                'status': 'active',
                'is_active': True
            }
        )
        
        if batch_created:
            self.stdout.write(self.style.SUCCESS(f'Created batch: {batch.batch_number}'))
            
            # Create initial stock-in movement
            StockMovement.objects.create(
                batch=batch,
                movement_type='in',
                quantity=500,
                reference='Initial Stock',
                notes='Initial stock receipt',
                created_by=user
            )
        
        # Create sample sales (stock out movements)
        sales_data = [
            {'quantity': 20, 'reference': 'Sale to Patient PT-000001', 'notes': 'Over the counter sale'},
            {'quantity': 15, 'reference': 'Sale to Patient PT-000002', 'notes': 'Prescription sale'},
            {'quantity': 10, 'reference': 'Sale to Walk-in Customer', 'notes': 'Cash sale'},
            {'quantity': 25, 'reference': 'Sale to Patient PT-000003', 'notes': 'Insurance claim'},
            {'quantity': 30, 'reference': 'Bulk Sale to Clinic ABC', 'notes': 'Corporate sale'},
        ]
        
        sales_created = 0
        for sale_data in sales_data:
            # Check if we have enough stock
            if batch.quantity_remaining >= sale_data['quantity']:
                # Create stock out movement (this will auto-update batch quantity)
                movement = StockMovement.objects.create(
                    batch=batch,
                    movement_type='out',
                    quantity=sale_data['quantity'],
                    reference=sale_data['reference'],
                    notes=sale_data['notes'],
                    created_by=user,
                    created_at=timezone.now() - timedelta(days=sales_created)
                )
                sales_created += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created sale: {sale_data["quantity"]} units - {sale_data["reference"]}'
                ))
        
        # Refresh batch to get updated quantity
        batch.refresh_from_db()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Sample data created successfully!\n'
            f'- Supplier: {supplier.name}\n'
            f'- Category: {category.name}\n'
            f'- Medication: {medication.name} {medication.strength}\n'
            f'- Batch: {batch.batch_number}\n'
            f'- Initial Stock: 500 units\n'
            f'- Sales Created: {sales_created} transactions\n'
            f'- Remaining Stock: {batch.quantity_remaining} units\n'
            f'\n📊 View sales at: /pharmacy/sales/'
        ))
