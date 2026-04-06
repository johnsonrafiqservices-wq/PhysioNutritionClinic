from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from pharmacy.models import Supplier, Category, Medication, Batch, StockMovement
from accounts.models import User
import random

class Command(BaseCommand):
    help = 'Add more sample pharmacy sales data'

    def handle(self, *args, **kwargs):
        # Get or create a user for the transactions
        user = User.objects.filter(is_staff=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No staff user found. Please create a user first.'))
            return
        
        # Get existing medications or create new ones
        medications_data = [
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'category_name': 'Pain Relief',
                'strength': '400mg',
                'form': 'tablet',
                'unit_price': 1500,
                'cost_price': 800,
                'selling_price': 1500,
                'stock': 400
            },
            {
                'name': 'Amoxicillin',
                'generic_name': 'Amoxicillin',
                'category_name': 'Antibiotics',
                'strength': '500mg',
                'form': 'capsule',
                'unit_price': 2000,
                'cost_price': 1000,
                'selling_price': 2000,
                'stock': 300
            },
            {
                'name': 'Ciprofloxacin',
                'generic_name': 'Ciprofloxacin',
                'category_name': 'Antibiotics',
                'strength': '500mg',
                'form': 'tablet',
                'unit_price': 2500,
                'cost_price': 1200,
                'selling_price': 2500,
                'stock': 250
            },
            {
                'name': 'Omeprazole',
                'generic_name': 'Omeprazole',
                'category_name': 'Gastrointestinal',
                'strength': '20mg',
                'form': 'capsule',
                'unit_price': 1800,
                'cost_price': 900,
                'selling_price': 1800,
                'stock': 200
            },
            {
                'name': 'Metformin',
                'generic_name': 'Metformin',
                'category_name': 'Diabetes',
                'strength': '500mg',
                'form': 'tablet',
                'unit_price': 1200,
                'cost_price': 600,
                'selling_price': 1200,
                'stock': 350
            },
        ]
        
        # Get or create supplier
        supplier = Supplier.objects.filter(is_active=True).first()
        if not supplier:
            supplier = Supplier.objects.create(
                name='MediSupply Uganda',
                contact_person='Sarah Nambi',
                email='sales@medisupply.ug',
                phone='+256 700 654321',
                address='Kampala, Uganda',
                is_active=True
            )
        
        batches = []
        for med_data in medications_data:
            # Get or create category
            category, _ = Category.objects.get_or_create(
                name=med_data['category_name'],
                defaults={'description': f'{med_data["category_name"]} medications'}
            )
            
            # Get or create medication
            medication, med_created = Medication.objects.get_or_create(
                name=med_data['name'],
                generic_name=med_data['generic_name'],
                defaults={
                    'category': category,
                    'strength': med_data['strength'],
                    'form': med_data['form'],
                    'reorder_level': 50,
                    'unit_price': med_data['unit_price'],
                    'unit_of_measure': 'Tablet' if med_data['form'] == 'tablet' else 'Capsule',
                    'manufacturer': 'Quality Pharma Ltd',
                    'requires_prescription': True if 'Antibiotic' in med_data['category_name'] else False,
                    'is_active': True
                }
            )
            
            if med_created:
                self.stdout.write(self.style.SUCCESS(f'Created medication: {medication.name}'))
            
            # Create batch
            batch_number = f'{med_data["name"][:4].upper()}2024{random.randint(100, 999)}'
            batch, batch_created = Batch.objects.get_or_create(
                batch_number=batch_number,
                defaults={
                    'medication': medication,
                    'supplier': supplier,
                    'quantity_remaining': med_data['stock'],
                    'cost_price': med_data['cost_price'],
                    'selling_price': med_data['selling_price'],
                    'manufacturing_date': datetime.now().date() - timedelta(days=120),
                    'expiry_date': datetime.now().date() + timedelta(days=500),
                    'received_by': user,
                    'invoice_number': f'INV-2024-{random.randint(100, 999)}',
                    'status': 'active',
                    'is_active': True
                }
            )
            
            if batch_created:
                # Create initial stock-in movement
                StockMovement.objects.create(
                    batch=batch,
                    movement_type='in',
                    quantity=med_data['stock'],
                    reference='Initial Stock',
                    notes='Stock receipt',
                    created_by=user
                )
                batches.append(batch)
        
        # Create multiple sales for each batch
        customer_types = [
            'Patient PT-{:06d}',
            'Walk-in Customer',
            'Insurance Patient',
            'Corporate Client',
            'Pharmacy Reseller'
        ]
        
        sales_notes = [
            'Over the counter sale',
            'Prescription sale',
            'Cash sale',
            'Insurance claim',
            'Corporate order',
            'Repeat prescription',
            'Emergency dispensing',
            'Bulk purchase'
        ]
        
        total_sales_created = 0
        total_revenue = 0
        
        for batch in batches:
            # Create 5-15 random sales per batch
            num_sales = random.randint(5, 15)
            
            for i in range(num_sales):
                # Random quantity between 5 and 50
                quantity = random.randint(5, 50)
                
                # Check if we have enough stock
                if batch.quantity_remaining >= quantity:
                    customer = random.choice(customer_types)
                    if 'PT-' in customer:
                        customer = customer.format(random.randint(1, 100))
                    
                    reference = f'Sale to {customer}'
                    notes = random.choice(sales_notes)
                    
                    # Random date within last 30 days
                    days_ago = random.randint(0, 30)
                    sale_date = timezone.now() - timedelta(days=days_ago)
                    
                    # Create stock out movement
                    movement = StockMovement.objects.create(
                        batch=batch,
                        movement_type='out',
                        quantity=quantity,
                        reference=reference,
                        notes=notes,
                        created_by=user,
                        created_at=sale_date
                    )
                    
                    revenue = quantity * batch.selling_price
                    total_revenue += revenue
                    total_sales_created += 1
                    
                    if i == 0:  # Print first sale for each medication
                        self.stdout.write(self.style.SUCCESS(
                            f'Sale: {batch.medication.name} - {quantity} units @ UGX {batch.selling_price} = UGX {revenue:,.0f}'
                        ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Sales data created successfully!\n'
            f'- Total Sales Transactions: {total_sales_created}\n'
            f'- Total Revenue Generated: UGX {total_revenue:,.0f}\n'
            f'- Medications with Sales: {len(batches)}\n'
            f'\n📊 View all sales at: /pharmacy/sales/'
        ))
