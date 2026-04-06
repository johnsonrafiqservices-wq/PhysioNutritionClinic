from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from pharmacy.models import (
    Category, Supplier, Medication, Batch, StockMovement, Prescription
)
from patients.models import Patient

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate pharmacy with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample pharmacy data...')
        
        # Get or create a user for operations
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.filter(role='admin').first()
            if not user:
                user = User.objects.first()
            
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting user: {e}'))
            return

        # Create Categories
        categories_data = [
            {'name': 'Pain Relief', 'description': 'Analgesics and pain management medications'},
            {'name': 'Antibiotics', 'description': 'Antimicrobial medications'},
            {'name': 'Cardiovascular', 'description': 'Heart and blood pressure medications'},
            {'name': 'Diabetes', 'description': 'Diabetes management medications'},
            {'name': 'Respiratory', 'description': 'Asthma and respiratory medications'},
            {'name': 'Gastrointestinal', 'description': 'Digestive system medications'},
            {'name': 'Vitamins & Supplements', 'description': 'Nutritional supplements'},
            {'name': 'Anti-inflammatory', 'description': 'Anti-inflammatory medications'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create Suppliers
        suppliers_data = [
            {
                'name': 'MedSupply Uganda Ltd',
                'contact_person': 'John Mukasa',
                'email': 'info@medsupply.ug',
                'phone': '+256 700 123456',
                'address': 'Plot 12, Industrial Area, Kampala'
            },
            {
                'name': 'Quality Pharma Distributors',
                'contact_person': 'Sarah Nakato',
                'email': 'sales@qualitypharma.ug',
                'phone': '+256 701 234567',
                'address': 'Ntinda Complex, Kampala'
            },
            {
                'name': 'East Africa Medical Supplies',
                'contact_person': 'David Okello',
                'email': 'orders@eams.co.ug',
                'phone': '+256 702 345678',
                'address': 'Lumumba Avenue, Kampala'
            },
        ]
        
        suppliers = {}
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults=sup_data
            )
            suppliers[sup_data['name']] = supplier
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created supplier: {supplier.name}'))

        # Create Medications
        medications_data = [
            {
                'name': 'Paracetamol',
                'generic_name': 'Acetaminophen',
                'category': 'Pain Relief',
                'strength': '500mg',
                'form': 'tablet',
                'unit_price': Decimal('1000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'Cipla Uganda',
                'reorder_level': 50,
                'requires_prescription': False
            },
            {
                'name': 'Amoxicillin',
                'generic_name': 'Amoxicillin',
                'category': 'Antibiotics',
                'strength': '500mg',
                'form': 'capsule',
                'unit_price': Decimal('5000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'GSK East Africa',
                'reorder_level': 30,
                'requires_prescription': True
            },
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'category': 'Anti-inflammatory',
                'strength': '400mg',
                'form': 'tablet',
                'unit_price': Decimal('2000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'Reckitt Benckiser',
                'reorder_level': 40,
                'requires_prescription': False
            },
            {
                'name': 'Metformin',
                'generic_name': 'Metformin HCl',
                'category': 'Diabetes',
                'strength': '500mg',
                'form': 'tablet',
                'unit_price': Decimal('3000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'Sanofi Uganda',
                'reorder_level': 25,
                'requires_prescription': True
            },
            {
                'name': 'Amlodipine',
                'generic_name': 'Amlodipine Besylate',
                'category': 'Cardiovascular',
                'strength': '5mg',
                'form': 'tablet',
                'unit_price': Decimal('4000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'Pfizer Uganda',
                'reorder_level': 20,
                'requires_prescription': True
            },
            {
                'name': 'Omeprazole',
                'generic_name': 'Omeprazole',
                'category': 'Gastrointestinal',
                'strength': '20mg',
                'form': 'capsule',
                'unit_price': Decimal('6000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'AstraZeneca',
                'reorder_level': 30,
                'requires_prescription': True
            },
            {
                'name': 'Salbutamol Inhaler',
                'generic_name': 'Salbutamol',
                'category': 'Respiratory',
                'strength': '100mcg',
                'form': 'inhaler',
                'unit_price': Decimal('15000.00'),
                'unit_of_measure': 'piece',
                'manufacturer': 'GSK',
                'reorder_level': 10,
                'requires_prescription': True
            },
            {
                'name': 'Multivitamin',
                'generic_name': 'Multivitamin Complex',
                'category': 'Vitamins & Supplements',
                'strength': '1 tablet daily',
                'form': 'tablet',
                'unit_price': Decimal('8000.00'),
                'unit_of_measure': 'bottle',
                'manufacturer': 'Centrum',
                'reorder_level': 15,
                'requires_prescription': False
            },
            {
                'name': 'Ciprofloxacin',
                'generic_name': 'Ciprofloxacin',
                'category': 'Antibiotics',
                'strength': '500mg',
                'form': 'tablet',
                'unit_price': Decimal('7000.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'Bayer',
                'reorder_level': 20,
                'requires_prescription': True
            },
            {
                'name': 'Diclofenac Gel',
                'generic_name': 'Diclofenac Sodium',
                'category': 'Anti-inflammatory',
                'strength': '1%',
                'form': 'ointment',
                'unit_price': Decimal('12000.00'),
                'unit_of_measure': 'tube',
                'manufacturer': 'Novartis',
                'reorder_level': 15,
                'requires_prescription': False
            },
        ]
        
        medications = {}
        for med_data in medications_data:
            category_name = med_data.pop('category')
            medication, created = Medication.objects.get_or_create(
                name=med_data['name'],
                strength=med_data['strength'],
                defaults={
                    **med_data,
                    'category': categories[category_name]
                }
            )
            medications[med_data['name']] = medication
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created medication: {medication.name}'))

        # Create Batches with stock
        batches_data = [
            {
                'medication': 'Paracetamol',
                'supplier': 'MedSupply Uganda Ltd',
                'batch_number': 'PAR-2024-001',
                'quantity_remaining': 200,
                'cost_price': Decimal('800.00'),
                'selling_price': Decimal('1000.00'),
                'expiry_date': date.today() + timedelta(days=365)
            },
            {
                'medication': 'Amoxicillin',
                'supplier': 'Quality Pharma Distributors',
                'batch_number': 'AMX-2024-001',
                'quantity_remaining': 150,
                'cost_price': Decimal('4000.00'),
                'selling_price': Decimal('5000.00'),
                'expiry_date': date.today() + timedelta(days=540)
            },
            {
                'medication': 'Ibuprofen',
                'supplier': 'MedSupply Uganda Ltd',
                'batch_number': 'IBU-2024-001',
                'quantity_remaining': 180,
                'cost_price': Decimal('1500.00'),
                'selling_price': Decimal('2000.00'),
                'expiry_date': date.today() + timedelta(days=450)
            },
            {
                'medication': 'Metformin',
                'supplier': 'East Africa Medical Supplies',
                'batch_number': 'MET-2024-001',
                'quantity_remaining': 100,
                'cost_price': Decimal('2500.00'),
                'selling_price': Decimal('3000.00'),
                'expiry_date': date.today() + timedelta(days=600)
            },
            {
                'medication': 'Amlodipine',
                'supplier': 'Quality Pharma Distributors',
                'batch_number': 'AML-2024-001',
                'quantity_remaining': 120,
                'cost_price': Decimal('3200.00'),
                'selling_price': Decimal('4000.00'),
                'expiry_date': date.today() + timedelta(days=720)
            },
            {
                'medication': 'Omeprazole',
                'supplier': 'East Africa Medical Supplies',
                'batch_number': 'OMP-2024-001',
                'quantity_remaining': 90,
                'cost_price': Decimal('5000.00'),
                'selling_price': Decimal('6000.00'),
                'expiry_date': date.today() + timedelta(days=480)
            },
            {
                'medication': 'Salbutamol Inhaler',
                'supplier': 'Quality Pharma Distributors',
                'batch_number': 'SAL-2024-001',
                'quantity_remaining': 50,
                'cost_price': Decimal('12000.00'),
                'selling_price': Decimal('15000.00'),
                'expiry_date': date.today() + timedelta(days=900)
            },
            {
                'medication': 'Multivitamin',
                'supplier': 'MedSupply Uganda Ltd',
                'batch_number': 'MUL-2024-001',
                'quantity_remaining': 75,
                'cost_price': Decimal('6500.00'),
                'selling_price': Decimal('8000.00'),
                'expiry_date': date.today() + timedelta(days=540)
            },
            {
                'medication': 'Ciprofloxacin',
                'supplier': 'East Africa Medical Supplies',
                'batch_number': 'CIP-2024-001',
                'quantity_remaining': 110,
                'cost_price': Decimal('5500.00'),
                'selling_price': Decimal('7000.00'),
                'expiry_date': date.today() + timedelta(days=650)
            },
            {
                'medication': 'Diclofenac Gel',
                'supplier': 'Quality Pharma Distributors',
                'batch_number': 'DIC-2024-001',
                'quantity_remaining': 60,
                'cost_price': Decimal('10000.00'),
                'selling_price': Decimal('12000.00'),
                'expiry_date': date.today() + timedelta(days=800)
            },
        ]
        
        for batch_data in batches_data:
            med_name = batch_data.pop('medication')
            sup_name = batch_data.pop('supplier')
            
            batch, created = Batch.objects.get_or_create(
                batch_number=batch_data['batch_number'],
                defaults={
                    **batch_data,
                    'medication': medications[med_name],
                    'supplier': suppliers[sup_name],
                    'received_by': user,
                    'status': 'active'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created batch: {batch.batch_number}'))

        # Add some low stock items (for testing alerts)
        low_stock_medications = [
            {
                'name': 'Aspirin',
                'generic_name': 'Acetylsalicylic Acid',
                'category': categories['Cardiovascular'],
                'strength': '75mg',
                'form': 'tablet',
                'unit_price': Decimal('1500.00'),
                'unit_of_measure': 'strip',
                'manufacturer': 'Bayer',
                'reorder_level': 50,
                'requires_prescription': False
            }
        ]
        
        for med_data in low_stock_medications:
            medication, created = Medication.objects.get_or_create(
                name=med_data['name'],
                strength=med_data['strength'],
                defaults=med_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created medication: {medication.name}'))
                
                # Create batch with low stock
                batch, batch_created = Batch.objects.get_or_create(
                    batch_number=f'ASP-2024-001',
                    defaults={
                        'medication': medication,
                        'supplier': list(suppliers.values())[0],
                        'quantity_remaining': 8,  # Below reorder level
                        'cost_price': Decimal('1200.00'),
                        'selling_price': Decimal('1500.00'),
                        'expiry_date': date.today() + timedelta(days=365),
                        'received_by': user,
                        'status': 'active'
                    }
                )
                if batch_created:
                    self.stdout.write(self.style.WARNING(f'Created low stock batch: {batch.batch_number}'))

        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Suppliers: {Supplier.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Medications: {Medication.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Batches: {Batch.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\nPharmacy sample data created successfully!'))
