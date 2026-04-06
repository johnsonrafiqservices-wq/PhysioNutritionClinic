#!/usr/bin/env python3
"""
Setup script for Physiotherapy & Nutrition Clinic Management System
This script automates the initial setup process for the clinic system.
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def setup_clinic_system():
    """Main setup function"""
    print("=" * 60)
    print("Physiotherapy & Nutrition Clinic Management System Setup")
    print("=" * 60)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
    
    # Step 1: Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Step 2: Create migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        return False
    
    # Step 3: Apply migrations
    if not run_command("python manage.py migrate", "Applying database migrations"):
        return False
    
    # Step 4: Create sample data
    print("\nCreating sample data...")
    try:
        django.setup()
        from django.contrib.auth import get_user_model
        from appointments.models import Service
        
        User = get_user_model()
        
        # Create default admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@clinic.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            print("✓ Default admin user created (admin/admin123)")
        
        # Create sample staff users
        staff_users = [
            {
                'username': 'dr_smith',
                'email': 'dr.smith@clinic.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'doctor'
            },
            {
                'username': 'nutritionist_jane',
                'email': 'jane@clinic.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'role': 'nutritionist'
            },
            {
                'username': 'receptionist_mary',
                'email': 'mary@clinic.com',
                'password': 'password123',
                'first_name': 'Mary',
                'last_name': 'Johnson',
                'role': 'receptionist'
            }
        ]
        
        for user_data in staff_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(**user_data)
                print(f"✓ Created user: {user_data['username']}")
        
        # Create sample services
        services = [
            {
                'name': 'Initial Physiotherapy Assessment',
                'category': 'physiotherapy',
                'description': 'Comprehensive initial assessment for new physiotherapy patients',
                'duration_minutes': 60,
                'base_price': 120.00
            },
            {
                'name': 'Physiotherapy Treatment Session',
                'category': 'physiotherapy',
                'description': 'Standard physiotherapy treatment session',
                'duration_minutes': 45,
                'base_price': 85.00
            },
            {
                'name': 'Nutrition Consultation',
                'category': 'nutrition',
                'description': 'Comprehensive nutrition assessment and planning',
                'duration_minutes': 60,
                'base_price': 100.00
            },
            {
                'name': 'Follow-up Nutrition Session',
                'category': 'nutrition',
                'description': 'Follow-up nutrition consultation',
                'duration_minutes': 30,
                'base_price': 60.00
            },
            {
                'name': 'Exercise Therapy',
                'category': 'treatment',
                'description': 'Supervised exercise therapy session',
                'duration_minutes': 30,
                'base_price': 50.00
            },
            {
                'name': 'Manual Therapy',
                'category': 'treatment',
                'description': 'Hands-on manual therapy treatment',
                'duration_minutes': 30,
                'base_price': 70.00
            }
        ]
        
        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                print(f"✓ Created service: {service_data['name']}")
        
        print("✓ Sample data created successfully")
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False
    
    # Step 5: Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠ Warning: Static files collection failed (this is normal in development)")
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\nOther test users:")
    print("- dr_smith / password123 (Doctor)")
    print("- nutritionist_jane / password123 (Nutritionist)")
    print("- receptionist_mary / password123 (Receptionist)")
    print("\nTo start the development server, run:")
    print("python manage.py runserver")
    print("\nThen visit: http://localhost:8000")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = setup_clinic_system()
    sys.exit(0 if success else 1)
