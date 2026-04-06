from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from pharmacy.models import Supplier, Category, Medication, Batch
from accounts.models import User
import random

class Command(BaseCommand):
    help = 'Populate pharmacy with comprehensive medication and batch data'

    def handle(self, *args, **kwargs):
        # Get or create a user for the transactions
        user = User.objects.filter(is_staff=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No staff user found. Please create a user first.'))
            return
        
        self.stdout.write(self.style.WARNING('Creating pharmacy data...'))
        
        # Create Suppliers
        suppliers_data = [
            {
                'name': 'PharmaCare Suppliers Ltd',
                'contact_person': 'John Mukasa',
                'email': 'info@pharmacare.ug',
                'phone': '+256 700 123456',
                'address': 'Kampala Road, Kampala, Uganda'
            },
            {
                'name': 'MediHealth Distributors',
                'contact_person': 'Sarah Nakato',
                'email': 'sales@medihealth.ug',
                'phone': '+256 750 234567',
                'address': 'Jinja Road, Kampala, Uganda'
            },
            {
                'name': 'Global Pharma Solutions',
                'contact_person': 'David Okello',
                'email': 'orders@globalpharma.ug',
                'phone': '+256 772 345678',
                'address': 'Industrial Area, Kampala, Uganda'
            }
        ]
        
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=data['name'],
                defaults={
                    'contact_person': data['contact_person'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'is_active': True
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created supplier: {supplier.name}'))
        
        # Create Categories
        categories_data = [
            {'name': 'Pain Relief', 'description': 'Pain relief and anti-inflammatory medications'},
            {'name': 'Antibiotics', 'description': 'Antibacterial medications'},
            {'name': 'Antihistamines', 'description': 'Allergy and cold medications'},
            {'name': 'Cardiovascular', 'description': 'Heart and blood pressure medications'},
            {'name': 'Diabetes', 'description': 'Blood sugar control medications'},
            {'name': 'Vitamins & Supplements', 'description': 'Nutritional supplements and vitamins'},
            {'name': 'Gastrointestinal', 'description': 'Digestive system medications'},
            {'name': 'Respiratory', 'description': 'Breathing and lung medications'}
        ]
        
        categories = {}
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            categories[data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))
        
        # Create Medications with Batches
        medications_data = [
            # Pain Relief
            {
                'name': 'Paracetamol', 'generic_name': 'Acetaminophen',
                'category': 'Pain Relief', 'strength': '500mg', 'form': 'tablet',
                'reorder_level': 100, 'unit_price': 500, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Quality Pharma Ltd', 'requires_prescription': False,
                'batches': [
                    {'quantity': 1000, 'cost': 300, 'price': 500, 'expiry_days': 365},
                    {'quantity': 500, 'cost': 300, 'price': 500, 'expiry_days': 540}
                ]
            },
            {
                'name': 'Ibuprofen', 'generic_name': 'Ibuprofen',
                'category': 'Pain Relief', 'strength': '400mg', 'form': 'tablet',
                'reorder_level': 80, 'unit_price': 800, 'unit_of_measure': 'Tablet',
                'manufacturer': 'MediCare Pharma', 'requires_prescription': False,
                'batches': [
                    {'quantity': 800, 'cost': 500, 'price': 800, 'expiry_days': 450}
                ]
            },
            {
                'name': 'Diclofenac', 'generic_name': 'Diclofenac Sodium',
                'category': 'Pain Relief', 'strength': '50mg', 'form': 'tablet',
                'reorder_level': 50, 'unit_price': 1000, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Global Health Ltd', 'requires_prescription': True,
                'batches': [
                    {'quantity': 600, 'cost': 600, 'price': 1000, 'expiry_days': 400}
                ]
            },
            # Antibiotics
            {
                'name': 'Amoxicillin', 'generic_name': 'Amoxicillin Trihydrate',
                'category': 'Antibiotics', 'strength': '500mg', 'form': 'capsule',
                'reorder_level': 100, 'unit_price': 1200, 'unit_of_measure': 'Capsule',
                'manufacturer': 'BioPharma Industries', 'requires_prescription': True,
                'batches': [
                    {'quantity': 750, 'cost': 700, 'price': 1200, 'expiry_days': 365},
                    {'quantity': 400, 'cost': 700, 'price': 1200, 'expiry_days': 500}
                ]
            },
            {
                'name': 'Ciprofloxacin', 'generic_name': 'Ciprofloxacin HCl',
                'category': 'Antibiotics', 'strength': '500mg', 'form': 'tablet',
                'reorder_level': 60, 'unit_price': 1500, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Advanced Pharma', 'requires_prescription': True,
                'batches': [
                    {'quantity': 500, 'cost': 900, 'price': 1500, 'expiry_days': 420}
                ]
            },
            {
                'name': 'Azithromycin', 'generic_name': 'Azithromycin',
                'category': 'Antibiotics', 'strength': '250mg', 'form': 'capsule',
                'reorder_level': 50, 'unit_price': 2000, 'unit_of_measure': 'Capsule',
                'manufacturer': 'MediCare Pharma', 'requires_prescription': True,
                'batches': [
                    {'quantity': 400, 'cost': 1200, 'price': 2000, 'expiry_days': 480}
                ]
            },
            # Antihistamines
            {
                'name': 'Cetirizine', 'generic_name': 'Cetirizine HCl',
                'category': 'Antihistamines', 'strength': '10mg', 'form': 'tablet',
                'reorder_level': 70, 'unit_price': 600, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Quality Pharma Ltd', 'requires_prescription': False,
                'batches': [
                    {'quantity': 600, 'cost': 350, 'price': 600, 'expiry_days': 365}
                ]
            },
            {
                'name': 'Loratadine', 'generic_name': 'Loratadine',
                'category': 'Antihistamines', 'strength': '10mg', 'form': 'tablet',
                'reorder_level': 60, 'unit_price': 700, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Global Health Ltd', 'requires_prescription': False,
                'batches': [
                    {'quantity': 500, 'cost': 400, 'price': 700, 'expiry_days': 400}
                ]
            },
            # Cardiovascular
            {
                'name': 'Amlodipine', 'generic_name': 'Amlodipine Besylate',
                'category': 'Cardiovascular', 'strength': '5mg', 'form': 'tablet',
                'reorder_level': 80, 'unit_price': 1000, 'unit_of_measure': 'Tablet',
                'manufacturer': 'CardioHealth Pharma', 'requires_prescription': True,
                'batches': [
                    {'quantity': 700, 'cost': 600, 'price': 1000, 'expiry_days': 540}
                ]
            },
            {
                'name': 'Atenolol', 'generic_name': 'Atenolol',
                'category': 'Cardiovascular', 'strength': '50mg', 'form': 'tablet',
                'reorder_level': 70, 'unit_price': 800, 'unit_of_measure': 'Tablet',
                'manufacturer': 'BioPharma Industries', 'requires_prescription': True,
                'batches': [
                    {'quantity': 600, 'cost': 500, 'price': 800, 'expiry_days': 450}
                ]
            },
            # Diabetes
            {
                'name': 'Metformin', 'generic_name': 'Metformin HCl',
                'category': 'Diabetes', 'strength': '500mg', 'form': 'tablet',
                'reorder_level': 100, 'unit_price': 1200, 'unit_of_measure': 'Tablet',
                'manufacturer': 'DiabeCare Ltd', 'requires_prescription': True,
                'batches': [
                    {'quantity': 900, 'cost': 700, 'price': 1200, 'expiry_days': 600},
                    {'quantity': 500, 'cost': 700, 'price': 1200, 'expiry_days': 500}
                ]
            },
            {
                'name': 'Glibenclamide', 'generic_name': 'Glibenclamide',
                'category': 'Diabetes', 'strength': '5mg', 'form': 'tablet',
                'reorder_level': 80, 'unit_price': 1000, 'unit_of_measure': 'Tablet',
                'manufacturer': 'MediCare Pharma', 'requires_prescription': True,
                'batches': [
                    {'quantity': 700, 'cost': 600, 'price': 1000, 'expiry_days': 480}
                ]
            },
            # Vitamins & Supplements
            {
                'name': 'Multivitamin', 'generic_name': 'Multivitamin Complex',
                'category': 'Vitamins & Supplements', 'strength': 'Standard', 'form': 'tablet',
                'reorder_level': 90, 'unit_price': 1500, 'unit_of_measure': 'Tablet',
                'manufacturer': 'VitaHealth Ltd', 'requires_prescription': False,
                'batches': [
                    {'quantity': 800, 'cost': 900, 'price': 1500, 'expiry_days': 730}
                ]
            },
            {
                'name': 'Vitamin C', 'generic_name': 'Ascorbic Acid',
                'category': 'Vitamins & Supplements', 'strength': '1000mg', 'form': 'tablet',
                'reorder_level': 100, 'unit_price': 800, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Quality Pharma Ltd', 'requires_prescription': False,
                'batches': [
                    {'quantity': 1000, 'cost': 500, 'price': 800, 'expiry_days': 650}
                ]
            },
            # Gastrointestinal
            {
                'name': 'Omeprazole', 'generic_name': 'Omeprazole',
                'category': 'Gastrointestinal', 'strength': '20mg', 'form': 'capsule',
                'reorder_level': 70, 'unit_price': 1500, 'unit_of_measure': 'Capsule',
                'manufacturer': 'GastroHealth Pharma', 'requires_prescription': True,
                'batches': [
                    {'quantity': 600, 'cost': 900, 'price': 1500, 'expiry_days': 450}
                ]
            },
            {
                'name': 'Loperamide', 'generic_name': 'Loperamide HCl',
                'category': 'Gastrointestinal', 'strength': '2mg', 'form': 'capsule',
                'reorder_level': 50, 'unit_price': 1000, 'unit_of_measure': 'Capsule',
                'manufacturer': 'MediCare Pharma', 'requires_prescription': False,
                'batches': [
                    {'quantity': 500, 'cost': 600, 'price': 1000, 'expiry_days': 400}
                ]
            },
            # Respiratory
            {
                'name': 'Salbutamol Inhaler', 'generic_name': 'Salbutamol Sulfate',
                'category': 'Respiratory', 'strength': '100mcg', 'form': 'inhaler',
                'reorder_level': 30, 'unit_price': 8000, 'unit_of_measure': 'Inhaler',
                'manufacturer': 'RespiCare Ltd', 'requires_prescription': True,
                'batches': [
                    {'quantity': 150, 'cost': 5000, 'price': 8000, 'expiry_days': 365}
                ]
            },
            {
                'name': 'Prednisolone', 'generic_name': 'Prednisolone',
                'category': 'Respiratory', 'strength': '5mg', 'form': 'tablet',
                'reorder_level': 60, 'unit_price': 1200, 'unit_of_measure': 'Tablet',
                'manufacturer': 'Advanced Pharma', 'requires_prescription': True,
                'batches': [
                    {'quantity': 500, 'cost': 700, 'price': 1200, 'expiry_days': 480}
                ]
            }
        ]
        
        created_count = 0
        batch_count = 0
        
        for med_data in medications_data:
            # Create medication
            medication, med_created = Medication.objects.get_or_create(
                name=med_data['name'],
                generic_name=med_data['generic_name'],
                defaults={
                    'category': categories[med_data['category']],
                    'strength': med_data['strength'],
                    'form': med_data['form'],
                    'reorder_level': med_data['reorder_level'],
                    'unit_price': Decimal(med_data['unit_price']),
                    'unit_of_measure': med_data['unit_of_measure'],
                    'manufacturer': med_data['manufacturer'],
                    'storage_instructions': 'Store in a cool, dry place away from direct sunlight',
                    'requires_prescription': med_data['requires_prescription'],
                    'is_active': True
                }
            )
            
            if med_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created medication: {medication.name} {medication.strength}'))
            
            # Create batches for this medication
            for idx, batch_data in enumerate(med_data['batches'], 1):
                supplier = random.choice(suppliers)
                batch_number = f'{medication.name[:3].upper()}-{datetime.now().year}-{random.randint(1000, 9999)}'
                
                batch, batch_created = Batch.objects.get_or_create(
                    batch_number=batch_number,
                    defaults={
                        'medication': medication,
                        'supplier': supplier,
                        'quantity_remaining': batch_data['quantity'],
                        'cost_price': Decimal(batch_data['cost']),
                        'selling_price': Decimal(batch_data['price']),
                        'manufacturing_date': datetime.now().date() - timedelta(days=180),
                        'expiry_date': datetime.now().date() + timedelta(days=batch_data['expiry_days']),
                        'received_by': user,
                        'invoice_number': f'INV-2024-{random.randint(1000, 9999)}',
                        'status': 'active',
                        'is_active': True,
                        'notes': 'Initial stock'
                    }
                )
                
                if batch_created:
                    batch_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created batch: {batch.batch_number} ({batch.quantity_remaining} units)'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully populated pharmacy database!\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'📦 Suppliers: {len(suppliers)}\n'
            f'📁 Categories: {len(categories)}\n'
            f'💊 Medications: {created_count} created ({Medication.objects.count()} total)\n'
            f'📋 Batches: {batch_count} created ({Batch.objects.count()} total)\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'🎯 Ready to record sales!\n'
            f'📊 Visit: /pharmacy/sales/\n'
        ))
