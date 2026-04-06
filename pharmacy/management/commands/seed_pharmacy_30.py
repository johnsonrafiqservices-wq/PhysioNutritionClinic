from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from pharmacy.models import Category, Supplier, Medication, Batch

User = get_user_model()


class Command(BaseCommand):
    help = 'Add ~30 pharmacy medications with suppliers, categories, and batches'

    def handle(self, *args, **options):
        self.stdout.write('Seeding pharmacy data (~30 medications)...\n')

        # Get a user for received_by
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return

        # ── Categories ───────────────────────────────────────────────
        cat_map = {}
        categories = [
            ('Pain Relief', 'Analgesics and pain management medications'),
            ('Antibiotics', 'Antimicrobial medications'),
            ('Cardiovascular', 'Heart and blood pressure medications'),
            ('Diabetes', 'Diabetes management medications'),
            ('Respiratory', 'Asthma and respiratory medications'),
            ('Gastrointestinal', 'Digestive system medications'),
            ('Vitamins & Supplements', 'Nutritional supplements'),
            ('Anti-inflammatory', 'Anti-inflammatory medications'),
            ('Dermatology', 'Skin care and dermatological medications'),
            ('Antimalarials', 'Malaria treatment and prophylaxis'),
        ]
        for name, desc in categories:
            obj, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
            cat_map[name] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'  + Category: {name}'))

        # ── Suppliers ────────────────────────────────────────────────
        sup_map = {}
        suppliers = [
            {
                'name': 'MedSupply Uganda Ltd',
                'contact_person': 'John Mukasa',
                'email': 'info@medsupply.ug',
                'phone': '+256 700 123456',
                'address': 'Plot 12, Industrial Area, Kampala',
            },
            {
                'name': 'Quality Pharma Distributors',
                'contact_person': 'Sarah Nakato',
                'email': 'sales@qualitypharma.ug',
                'phone': '+256 701 234567',
                'address': 'Ntinda Complex, Kampala',
            },
            {
                'name': 'East Africa Medical Supplies',
                'contact_person': 'David Okello',
                'email': 'orders@eams.co.ug',
                'phone': '+256 702 345678',
                'address': 'Lumumba Avenue, Kampala',
            },
            {
                'name': 'NilePharma International',
                'contact_person': 'Grace Apio',
                'email': 'grace@nilepharma.ug',
                'phone': '+256 703 456789',
                'address': 'Plot 45, Jinja Road, Kampala',
            },
            {
                'name': 'HealthLink Distributors',
                'contact_person': 'Peter Ssemakula',
                'email': 'peter@healthlink.ug',
                'phone': '+256 704 567890',
                'address': 'Wandegeya, Kampala',
            },
        ]
        for s in suppliers:
            obj, created = Supplier.objects.get_or_create(name=s['name'], defaults=s)
            sup_map[s['name']] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'  + Supplier: {s["name"]}'))

        sup_list = list(sup_map.values())

        # ── Medications ──────────────────────────────────────────────
        meds_data = [
            # Pain Relief
            ('Paracetamol', 'Acetaminophen', 'Pain Relief', '500mg', 'tablet', 1000, 'strip', 'Cipla Uganda', 50, False),
            ('Tramadol', 'Tramadol HCl', 'Pain Relief', '50mg', 'capsule', 3500, 'strip', 'Sanofi Uganda', 20, True),
            ('Morphine Sulfate', 'Morphine', 'Pain Relief', '10mg', 'injection', 25000, 'ampoule', 'Martindale Pharma', 10, True),
            # Antibiotics
            ('Amoxicillin', 'Amoxicillin', 'Antibiotics', '500mg', 'capsule', 5000, 'strip', 'GSK East Africa', 30, True),
            ('Ciprofloxacin', 'Ciprofloxacin', 'Antibiotics', '500mg', 'tablet', 7000, 'strip', 'Bayer', 20, True),
            ('Azithromycin', 'Azithromycin', 'Antibiotics', '250mg', 'tablet', 8000, 'strip', 'Pfizer Uganda', 20, True),
            ('Metronidazole', 'Metronidazole', 'Antibiotics', '400mg', 'tablet', 3000, 'strip', 'Cipla Uganda', 30, True),
            ('Doxycycline', 'Doxycycline Hyclate', 'Antibiotics', '100mg', 'capsule', 4500, 'strip', 'Quality Chemicals', 25, True),
            ('Ceftriaxone', 'Ceftriaxone Sodium', 'Antibiotics', '1g', 'injection', 12000, 'vial', 'Roche Uganda', 15, True),
            ('Erythromycin', 'Erythromycin Stearate', 'Antibiotics', '500mg', 'tablet', 6000, 'strip', 'Abbott', 20, True),
            # Cardiovascular
            ('Amlodipine', 'Amlodipine Besylate', 'Cardiovascular', '5mg', 'tablet', 4000, 'strip', 'Pfizer Uganda', 20, True),
            ('Atenolol', 'Atenolol', 'Cardiovascular', '50mg', 'tablet', 3500, 'strip', 'AstraZeneca', 25, True),
            ('Losartan', 'Losartan Potassium', 'Cardiovascular', '50mg', 'tablet', 5500, 'strip', 'Merck', 20, True),
            ('Aspirin', 'Acetylsalicylic Acid', 'Cardiovascular', '75mg', 'tablet', 1500, 'strip', 'Bayer', 50, False),
            ('Hydrochlorothiazide', 'Hydrochlorothiazide', 'Cardiovascular', '25mg', 'tablet', 2500, 'strip', 'Novartis', 30, True),
            # Diabetes
            ('Metformin', 'Metformin HCl', 'Diabetes', '500mg', 'tablet', 3000, 'strip', 'Sanofi Uganda', 25, True),
            ('Glibenclamide', 'Glibenclamide', 'Diabetes', '5mg', 'tablet', 2500, 'strip', 'Cipla Uganda', 25, True),
            ('Insulin Mixtard', 'Human Insulin 70/30', 'Diabetes', '100IU/ml', 'injection', 35000, 'vial', 'Novo Nordisk', 10, True),
            # Respiratory
            ('Salbutamol Inhaler', 'Salbutamol', 'Respiratory', '100mcg', 'inhaler', 15000, 'piece', 'GSK', 10, True),
            ('Aminophylline', 'Aminophylline', 'Respiratory', '100mg', 'tablet', 2000, 'strip', 'Cipla Uganda', 20, True),
            # Gastrointestinal
            ('Omeprazole', 'Omeprazole', 'Gastrointestinal', '20mg', 'capsule', 6000, 'strip', 'AstraZeneca', 30, True),
            ('Oral Rehydration Salts', 'ORS', 'Gastrointestinal', '20.5g', 'powder', 1500, 'sachet', 'Quality Chemicals', 100, False),
            ('Loperamide', 'Loperamide HCl', 'Gastrointestinal', '2mg', 'capsule', 2500, 'strip', 'Johnson & Johnson', 30, False),
            # Anti-inflammatory
            ('Ibuprofen', 'Ibuprofen', 'Anti-inflammatory', '400mg', 'tablet', 2000, 'strip', 'Reckitt Benckiser', 40, False),
            ('Diclofenac Gel', 'Diclofenac Sodium', 'Anti-inflammatory', '1%', 'ointment', 12000, 'tube', 'Novartis', 15, False),
            ('Prednisolone', 'Prednisolone', 'Anti-inflammatory', '5mg', 'tablet', 4000, 'strip', 'Pfizer Uganda', 20, True),
            # Vitamins & Supplements
            ('Multivitamin', 'Multivitamin Complex', 'Vitamins & Supplements', '1 tablet daily', 'tablet', 8000, 'bottle', 'Centrum', 15, False),
            ('Ferrous Sulphate', 'Iron Supplement', 'Vitamins & Supplements', '200mg', 'tablet', 2500, 'strip', 'Quality Chemicals', 40, False),
            ('Folic Acid', 'Folic Acid', 'Vitamins & Supplements', '5mg', 'tablet', 1500, 'strip', 'Cipla Uganda', 40, False),
            # Dermatology
            ('Clotrimazole Cream', 'Clotrimazole', 'Dermatology', '1%', 'cream', 5000, 'tube', 'Bayer', 20, False),
            ('Hydrocortisone Cream', 'Hydrocortisone', 'Dermatology', '1%', 'cream', 7000, 'tube', 'GSK East Africa', 15, True),
            # Antimalarials
            ('Artemether-Lumefantrine', 'AL (Coartem)', 'Antimalarials', '20/120mg', 'tablet', 6000, 'pack', 'Novartis', 50, True),
            ('Quinine', 'Quinine Dihydrochloride', 'Antimalarials', '300mg', 'injection', 8000, 'ampoule', 'Quality Chemicals', 20, True),
        ]

        med_map = {}
        created_count = 0
        for (name, generic, cat, strength, form, price, uom, mfr, reorder, rx) in meds_data:
            obj, created = Medication.objects.get_or_create(
                name=name,
                strength=strength,
                defaults={
                    'generic_name': generic,
                    'category': cat_map[cat],
                    'form': form,
                    'unit_price': Decimal(str(price)),
                    'unit_of_measure': uom,
                    'manufacturer': mfr,
                    'reorder_level': reorder,
                    'requires_prescription': rx,
                    'is_active': True,
                }
            )
            med_map[name] = obj
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'  Medications: {created_count} new / {len(meds_data)} total defined'))

        # ── Batches (one per medication, a few get a 2nd batch) ──────
        today = date.today()
        batch_count = 0
        for med_name, med_obj in med_map.items():
            prefix = ''.join(c for c in med_name[:3].upper() if c.isalpha())
            bn = f'{prefix}-2025-001'

            qty = random.randint(40, 250)
            cost = float(med_obj.unit_price) * random.uniform(0.6, 0.85)
            sell = float(med_obj.unit_price)
            exp_days = random.randint(180, 730)

            _, created = Batch.objects.get_or_create(
                batch_number=bn,
                defaults={
                    'medication': med_obj,
                    'supplier': random.choice(sup_list),
                    'quantity_remaining': qty,
                    'cost_price': Decimal(str(round(cost, 2))),
                    'selling_price': Decimal(str(round(sell, 2))),
                    'manufacturing_date': today - timedelta(days=random.randint(30, 180)),
                    'expiry_date': today + timedelta(days=exp_days),
                    'received_by': user,
                    'status': 'active',
                    'is_active': True,
                }
            )
            if created:
                batch_count += 1

        # Add a 2nd batch for some popular meds (simulates multiple deliveries)
        popular = ['Paracetamol', 'Amoxicillin', 'Metformin', 'Artemether-Lumefantrine',
                    'Omeprazole', 'Ibuprofen', 'Ciprofloxacin', 'Ferrous Sulphate']
        for med_name in popular:
            if med_name not in med_map:
                continue
            med_obj = med_map[med_name]
            prefix = ''.join(c for c in med_name[:3].upper() if c.isalpha())
            bn = f'{prefix}-2025-002'
            qty = random.randint(20, 120)
            cost = float(med_obj.unit_price) * random.uniform(0.6, 0.85)
            sell = float(med_obj.unit_price)
            exp_days = random.randint(270, 900)

            _, created = Batch.objects.get_or_create(
                batch_number=bn,
                defaults={
                    'medication': med_obj,
                    'supplier': random.choice(sup_list),
                    'quantity_remaining': qty,
                    'cost_price': Decimal(str(round(cost, 2))),
                    'selling_price': Decimal(str(round(sell, 2))),
                    'manufacturing_date': today - timedelta(days=random.randint(10, 90)),
                    'expiry_date': today + timedelta(days=exp_days),
                    'received_by': user,
                    'status': 'active',
                    'is_active': True,
                }
            )
            if created:
                batch_count += 1

        # Add a couple of low-stock batches for alert testing
        low_stock_meds = ['Morphine Sulfate', 'Insulin Mixtard', 'Ceftriaxone']
        for med_name in low_stock_meds:
            if med_name not in med_map:
                continue
            med_obj = med_map[med_name]
            prefix = ''.join(c for c in med_name[:3].upper() if c.isalpha())
            bn = f'{prefix}-2025-LOW'
            _, created = Batch.objects.get_or_create(
                batch_number=bn,
                defaults={
                    'medication': med_obj,
                    'supplier': random.choice(sup_list),
                    'quantity_remaining': random.randint(2, 8),
                    'cost_price': Decimal(str(round(float(med_obj.unit_price) * 0.7, 2))),
                    'selling_price': med_obj.unit_price,
                    'manufacturing_date': today - timedelta(days=60),
                    'expiry_date': today + timedelta(days=random.randint(45, 120)),
                    'received_by': user,
                    'status': 'active',
                    'is_active': True,
                }
            )
            if created:
                batch_count += 1

        self.stdout.write(self.style.SUCCESS(f'  Batches: {batch_count} new'))

        # ── Summary ──────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 40))
        self.stdout.write(self.style.SUCCESS(f'  Categories    : {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Suppliers     : {Supplier.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Medications   : {Medication.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Batches       : {Batch.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('═' * 40))
        self.stdout.write(self.style.SUCCESS('Pharmacy seeding complete!'))
