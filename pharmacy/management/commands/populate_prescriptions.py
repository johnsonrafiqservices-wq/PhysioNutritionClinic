from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pharmacy.models import Prescription, PrescriptionItem, Medication, Batch
from patients.models import Patient
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample prescriptions with medications for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating sample prescriptions...'))
        
        # Get or create a doctor user
        doctor = User.objects.filter(role='doctor').first()
        if not doctor:
            self.stdout.write(self.style.WARNING('No doctor user found, creating one...'))
            doctor = User.objects.create_user(
                username='dr_smith',
                email='doctor@clinic.com',
                password='password123',
                first_name='John',
                last_name='Smith',
                role='doctor'
            )
            self.stdout.write(self.style.SUCCESS(f'Created doctor: {doctor.username}'))
        
        # Get or create sample patients
        patients = list(Patient.objects.all()[:5])
        if not patients:
            self.stdout.write(self.style.WARNING('No patients found. Please create patients first.'))
            return
        
        # Get available medications with stock
        medications = list(Medication.objects.filter(
            batches__is_active=True,
            batches__quantity_remaining__gt=0
        ).distinct()[:10])
        
        if not medications:
            self.stdout.write(self.style.ERROR('No medications with stock found. Please run populate_medications first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(medications)} medications with stock'))
        
        # Delete existing pending prescriptions
        deleted_count = Prescription.objects.filter(status='pending').delete()[0]
        self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing pending prescriptions'))
        
        prescriptions_created = 0
        
        # Create 10 sample prescriptions
        for i in range(10):
            patient = random.choice(patients)
            
            # 70% single medication, 30% multi-medication
            if random.random() < 0.7:
                # Single medication prescription (legacy style)
                medication = random.choice(medications)
                
                # Get a batch with stock for this medication
                batch = Batch.objects.filter(
                    medication=medication,
                    is_active=True,
                    quantity_remaining__gt=0
                ).first()
                
                if not batch:
                    continue
                
                quantity = random.randint(5, min(30, batch.quantity_remaining))
                
                prescription = Prescription.objects.create(
                    patient=patient,
                    medication=medication,
                    dosage=random.choice(['500mg', '250mg', '10mg', '5mg', '100mg']),
                    frequency=random.choice(['Once daily', 'Twice daily', 'Three times daily', 'As needed']),
                    duration=random.choice(['5 days', '7 days', '10 days', '14 days', '30 days']),
                    quantity=quantity,
                    instructions=f'Take {random.choice(["with food", "before meals", "after meals", "at bedtime"])}',
                    status='pending',
                    prescribed_by=doctor,
                    prescribed_date=timezone.now()
                )
                
                prescriptions_created += 1
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created prescription #{prescriptions_created}: {patient.get_full_name()} - '
                    f'{medication.name} x{quantity} (Total: UGX {batch.selling_price * quantity:,.0f})'
                ))
            
            else:
                # Multi-medication prescription
                prescription = Prescription.objects.create(
                    patient=patient,
                    instructions='Follow dosage instructions for each medication',
                    status='pending',
                    prescribed_by=doctor,
                    prescribed_date=timezone.now()
                )
                
                # Add 2-4 medications to this prescription
                num_meds = random.randint(2, 4)
                selected_meds = random.sample(medications, min(num_meds, len(medications)))
                
                total_amount = 0
                for medication in selected_meds:
                    # Get a batch with stock
                    batch = Batch.objects.filter(
                        medication=medication,
                        is_active=True,
                        quantity_remaining__gt=0
                    ).first()
                    
                    if not batch:
                        continue
                    
                    quantity = random.randint(5, min(30, batch.quantity_remaining))
                    
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        medication=medication,
                        dosage=random.choice(['500mg', '250mg', '10mg', '5mg', '100mg']),
                        frequency=random.choice(['Once daily', 'Twice daily', 'Three times daily', 'As needed']),
                        duration=random.choice(['5 days', '7 days', '10 days', '14 days', '30 days']),
                        quantity=quantity,
                        notes=f'Take {random.choice(["with food", "before meals", "after meals", "at bedtime"])}'
                    )
                    
                    total_amount += batch.selling_price * quantity
                
                prescriptions_created += 1
                item_count = prescription.items.count()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created multi-med prescription #{prescriptions_created}: {patient.get_full_name()} - '
                    f'{item_count} medications (Total: UGX {total_amount:,.0f})'
                ))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {prescriptions_created} sample prescriptions!'))
        self.stdout.write(self.style.SUCCESS('You can now test the prescription dispensing feature in the sales dashboard.'))
