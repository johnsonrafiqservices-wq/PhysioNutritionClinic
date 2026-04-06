"""
Seed script to populate the database with sample data
Run with: python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from accounts.models import User
from patients.models import Patient
from datetime import date, timedelta
import random

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        'admin', 
        'admin@clinic.com', 
        'admin123', 
        first_name='Admin', 
        last_name='User', 
        role='admin'
    )
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')

# Sample patient data
patients_data = [
    {'first_name': 'John', 'last_name': 'Mukasa', 'gender': 'M', 'phone': '0701234567'},
    {'first_name': 'Sarah', 'last_name': 'Nakamya', 'gender': 'F', 'phone': '0702345678'},
    {'first_name': 'Peter', 'last_name': 'Okello', 'gender': 'M', 'phone': '0703456789'},
    {'first_name': 'Grace', 'last_name': 'Namutebi', 'gender': 'F', 'phone': '0704567890'},
    {'first_name': 'David', 'last_name': 'Ssekandi', 'gender': 'M', 'phone': '0705678901'},
    {'first_name': 'Mary', 'last_name': 'Amongi', 'gender': 'F', 'phone': '0706789012'},
    {'first_name': 'James', 'last_name': 'Tumusiime', 'gender': 'M', 'phone': '0707890123'},
    {'first_name': 'Agnes', 'last_name': 'Nalwoga', 'gender': 'F', 'phone': '0708901234'},
    {'first_name': 'Robert', 'last_name': 'Byaruhanga', 'gender': 'M', 'phone': '0709012345'},
    {'first_name': 'Joyce', 'last_name': 'Akello', 'gender': 'F', 'phone': '0710123456'},
]

for i, data in enumerate(patients_data):
    # Check if patient already exists by name
    if Patient.objects.filter(first_name=data['first_name'], last_name=data['last_name']).exists():
        print(f"Patient {data['first_name']} {data['last_name']} already exists, skipping...")
        continue
    
    dob = date.today() - timedelta(days=random.randint(7300, 21900))
    
    # Generate unique patient_id
    last_patient = Patient.objects.order_by('-id').first()
    next_num = (last_patient.id + 1) if last_patient else 1
    patient_id = f"PT-{next_num:06d}"
    
    patient = Patient.objects.create(
        patient_id=patient_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data['gender'],
        phone=data['phone'],
        date_of_birth=dob,
        email=f"{data['first_name'].lower()}.{data['last_name'].lower()}@email.com",
    )
    print(f'Created patient: {patient.get_full_name()} ({patient.patient_id})')

print(f'\nTotal patients: {Patient.objects.count()}')
print('\n--- Login Credentials ---')
print('Username: admin')
print('Password: admin123')
