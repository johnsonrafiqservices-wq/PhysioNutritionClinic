# Physiotherapy & Nutrition Clinic Management System

A comprehensive Django-based clinic management system designed for physiotherapy and nutrition clinics. This system provides role-based access control, patient management, appointment scheduling, billing, and reporting capabilities.

## Features

### 🏥 Core Functionality
- **Patient Management**: Complete patient registration, demographics, medical history, and document storage
- **Appointment Scheduling**: Book, manage, and track appointments with different service providers
- **Billing & Payments**: Invoice generation, payment processing, insurance claims, and payment plans
- **Medical Records**: Digital medical records, treatment notes, and document management
- **Reporting & Analytics**: Comprehensive reports for patients, appointments, and financial data

### 👥 Role-Based Access Control
- **Administrator**: Full system access and user management
- **Doctor/Physiotherapist**: Patient care, treatment notes, and medical records
- **Nutritionist**: Nutrition consultations and meal planning
- **Receptionist**: Patient registration, appointment scheduling, and basic billing
- **Nurse**: Vital signs recording, triage assessments, and patient care support
- **Billing Staff**: Invoice management, payment processing, and financial reports

### 📋 Clinical Workflows
- **Patient Registration**: Comprehensive intake forms with demographics, insurance, and medical history
- **Vital Signs Recording**: Height, weight, blood pressure, heart rate, temperature, and BMI calculation
- **Triage Assessment**: Priority-based patient assessment with pain scales and symptom tracking
- **Treatment Sessions**: Detailed treatment notes, progress tracking, and home exercise prescriptions
- **Nutrition Consultations**: Dietary assessments, meal planning, and supplement recommendations

### 💰 Financial Management
- **Invoice Generation**: Automated invoice creation with line items and tax calculations
- **Payment Processing**: Multiple payment methods (cash, card, check, bank transfer, insurance)
- **Insurance Claims**: Submit and track insurance claims with approval workflows
- **Payment Plans**: Flexible payment plan options for patients
- **PDF Generation**: Professional invoice and receipt generation

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Clone and Setup
```bash
# Navigate to the project directory
cd C:\Users\it.sm\CascadeProjects\PhysioNutritionClinic

# Create a virtual environment (recommended)
python -m venv clinic_env

# Activate virtual environment
# On Windows:
clinic_env\Scripts\activate
# On macOS/Linux:
source clinic_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Setup
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### Step 3: Load Initial Data (Optional)
```bash
# Create sample services
python manage.py shell
```

In the Django shell, run:
```python
from appointments.models import Service

# Create sample services
services = [
    {'name': 'Initial Physiotherapy Assessment', 'category': 'physiotherapy', 'duration_minutes': 60, 'base_price': 120.00},
    {'name': 'Physiotherapy Treatment Session', 'category': 'physiotherapy', 'duration_minutes': 45, 'base_price': 85.00},
    {'name': 'Nutrition Consultation', 'category': 'nutrition', 'duration_minutes': 60, 'base_price': 100.00},
    {'name': 'Follow-up Nutrition Session', 'category': 'nutrition', 'duration_minutes': 30, 'base_price': 60.00},
    {'name': 'Exercise Therapy', 'category': 'treatment', 'duration_minutes': 30, 'base_price': 50.00},
]

for service_data in services:
    Service.objects.get_or_create(**service_data)

exit()
```

### Step 4: Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

## System Architecture

### Apps Structure
```
clinic_system/
├── accounts/          # User authentication and role management
├── patients/          # Patient management and vital signs
├── appointments/      # Appointment scheduling and treatment sessions
├── billing/           # Invoicing, payments, and insurance
├── medical_records/   # Medical records and document management
├── reports/           # Analytics and reporting
└── templates/         # HTML templates for the web interface
```

### Database Models

#### Core Models
- **User**: Extended Django user model with role-based permissions
- **Patient**: Complete patient demographics and medical information
- **Appointment**: Scheduling system with service providers
- **Service**: Clinic services with pricing and duration
- **Invoice**: Billing system with line items and tax calculations
- **Payment**: Payment tracking with multiple payment methods

#### Clinical Models
- **VitalSigns**: Patient vital measurements with automatic BMI calculation
- **TriageAssessment**: Priority-based patient assessment system
- **TreatmentSession**: Detailed treatment notes and progress tracking
- **NutritionConsultation**: Dietary assessments and meal planning
- **MedicalRecord**: Digital medical records and clinical notes
- **Document**: File storage for patient documents and images

## Usage Guide

### For Receptionists
1. **Register New Patients**: Use the patient registration form to collect complete demographics
2. **Schedule Appointments**: Book appointments with available providers
3. **Record Vital Signs**: Measure and record patient vitals before appointments
4. **Process Payments**: Handle payment collection and invoice generation

### For Clinical Staff (Doctors/Physiotherapists/Nutritionists)
1. **Review Patient Information**: Access complete patient history and previous treatments
2. **Conduct Triage Assessments**: Prioritize patients based on clinical needs
3. **Document Treatment Sessions**: Record detailed treatment notes and patient responses
4. **Create Medical Records**: Maintain comprehensive clinical documentation
5. **Generate Reports**: Access patient progress and treatment outcome reports

### For Billing Staff
1. **Create Invoices**: Generate detailed invoices for services provided
2. **Process Payments**: Record payments using various payment methods
3. **Manage Insurance Claims**: Submit and track insurance claim processing
4. **Setup Payment Plans**: Create flexible payment arrangements for patients
5. **Generate Financial Reports**: Monitor clinic revenue and outstanding balances

### For Administrators
1. **User Management**: Create and manage staff accounts with appropriate roles
2. **System Configuration**: Configure services, pricing, and clinic settings
3. **Data Analytics**: Access comprehensive reports and system analytics
4. **Backup Management**: Ensure regular data backups and system maintenance

## Security Features

- **Role-Based Access Control**: Granular permissions based on user roles
- **Data Encryption**: Secure storage of sensitive patient information
- **Audit Trails**: Complete logging of user actions and data changes
- **Session Management**: Secure user sessions with automatic timeout
- **CSRF Protection**: Built-in protection against cross-site request forgery

## Customization

### Adding New Services
1. Access Django Admin at `/admin/`
2. Navigate to Appointments > Services
3. Add new services with appropriate categories and pricing

### Modifying User Roles
Edit the `ROLES` dictionary in `clinic_system/settings.py` to add or modify user roles.

### Custom Reports
Add new report views in the `reports/views.py` file and corresponding templates.

## Backup and Maintenance

### Database Backup
```bash
# Create database backup
python manage.py dumpdata > clinic_backup.json

# Restore from backup
python manage.py loaddata clinic_backup.json
```

### Regular Maintenance
- Monitor system logs for errors
- Regularly update dependencies
- Perform database maintenance
- Review user access permissions
- Backup patient data regularly

## Support and Documentation

### Technical Support
- Check Django documentation for framework-specific issues
- Review model definitions in each app's `models.py` file
- Examine view logic in `views.py` files for business logic

### Troubleshooting
- Ensure all dependencies are installed correctly
- Check database connectivity and migrations
- Verify user permissions for role-based access issues
- Review Django logs for detailed error information

## License

This clinic management system is designed for internal use. Ensure compliance with healthcare data protection regulations (HIPAA, GDPR, etc.) when deploying in production environments.

## Contributing

When modifying the system:
1. Follow Django best practices
2. Maintain role-based access controls
3. Update documentation for new features
4. Test thoroughly before deployment
5. Ensure patient data privacy and security
