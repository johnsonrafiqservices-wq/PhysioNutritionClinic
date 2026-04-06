# PhysioNutrition Clinic - System Roles Guide

## Overview
This document outlines all user roles in the PhysioNutrition Clinic Management System and their access to different application modules.

---

## Role Categories & Applications Access

### 1. **Administration & Management**

#### System Administrator (`admin`)
- **Full system access**
- All applications: ✅ Full CRUD
- User management and system configuration
- **Apps**: All modules

#### Clinic Manager (`clinic_manager`)
- **Clinic operations oversight**
- All applications: ✅ Read/Write (except system settings)
- Staff scheduling and resource allocation
- **Apps**: All modules except system administration

#### Medical Director (`medical_director`)
- **Clinical oversight and quality assurance**
- Medical operations and clinical protocols
- **Apps**: Patients, Appointments, Medical Records, Laboratory, Pharmacy, Reports

---

### 2. **Clinical Staff** (Patients & Appointments Apps)

#### Doctor/General Practitioner (`doctor`)
- Patient assessments and diagnosis
- Prescription writing
- Medical record management
- **Apps**: Patients ✅, Appointments ✅, Medical Records ✅, Laboratory ✅, Pharmacy ✅

#### Physiotherapist (`physiotherapist`)
- Physiotherapy assessments
- Treatment planning and sessions
- Progress tracking
- **Apps**: Patients ✅, Appointments ✅, Medical Records ✅

#### Nutritionist/Dietitian (`nutritionist`)
- Nutritional assessments
- Dietary planning
- Nutrition consultations
- **Apps**: Patients ✅, Appointments ✅, Medical Records ✅

#### Nurse (`nurse`)
- Vital signs recording
- Patient triage
- Treatment assistance
- **Apps**: Patients ✅, Appointments ✅, Medical Records ✅, Laboratory 📖

#### Clinical Assistant (`clinical_assistant`)
- Patient assistance
- Basic data entry
- Appointment support
- **Apps**: Patients 📖, Appointments ✅, Medical Records 📖

---

### 3. **Reception & Front Desk** (Appointments & Patient Registration)

#### Receptionist (`receptionist`)
- Patient registration
- Appointment scheduling
- Front desk operations
- **Apps**: Patients ✅, Appointments ✅, Billing 📖

#### Front Desk Officer (`front_desk`)
- Check-in/check-out
- Appointment confirmation
- Basic patient information
- **Apps**: Patients ✅, Appointments ✅

#### Appointment Coordinator (`appointment_coordinator`)
- Appointment management
- Schedule optimization
- Provider coordination
- **Apps**: Appointments ✅, Patients 📖, Staff Management 📖

---

### 4. **Laboratory** (Laboratory App)

#### Laboratory Technician (`lab_technician`)
- Lab test processing
- Sample collection
- Result entry
- **Apps**: Laboratory ✅, Patients 📖

#### Laboratory Manager (`lab_manager`)
- Lab operations management
- Quality control
- Equipment maintenance
- **Apps**: Laboratory ✅, Patients 📖, Reports 📖

#### Pathologist (`pathologist`)
- Lab result interpretation
- Report approval
- Clinical correlation
- **Apps**: Laboratory ✅, Patients 📖, Medical Records 📖

---

### 5. **Pharmacy** (Pharmacy App)

#### Pharmacist (`pharmacist`)
- Prescription dispensing
- Drug counseling
- Inventory management
- **Apps**: Pharmacy ✅, Patients 📖, Appointments 📖

#### Pharmacy Assistant (`pharmacy_assistant`)
- Medication dispensing
- Stock tracking
- Basic patient interaction
- **Apps**: Pharmacy ✅

#### Pharmacy Manager (`pharmacy_manager`)
- Pharmacy operations
- Drug procurement
- Staff supervision
- **Apps**: Pharmacy ✅, Budget 📖, Reports 📖

---

### 6. **Billing & Finance** (Billing App)

#### Billing Officer (`billing_officer`)
- Invoice generation
- Payment processing
- Insurance claims
- **Apps**: Billing ✅, Patients 📖, Appointments 📖

#### Accountant (`accountant`)
- Financial records
- Revenue tracking
- Account reconciliation
- **Apps**: Billing ✅, Budget ✅, Reports ✅

#### Finance Manager (`finance_manager`)
- Financial planning
- Budget oversight
- Financial reports
- **Apps**: Billing ✅, Budget ✅, Reports ✅

#### Cashier (`cashier`)
- Payment collection
- Receipt generation
- Daily cash reconciliation
- **Apps**: Billing ✅

---

### 7. **Medical Records** (Medical Records App)

#### Medical Records Officer (`medical_records_officer`)
- Record management
- Document filing
- Record retrieval
- **Apps**: Medical Records ✅, Patients 📖

#### Records Manager (`records_manager`)
- Records department oversight
- Archive management
- Compliance monitoring
- **Apps**: Medical Records ✅, Patients 📖, Reports 📖

#### Data Entry Clerk (`data_entry_clerk`)
- Data entry
- Record digitization
- Basic filing
- **Apps**: Medical Records ✅

---

### 8. **Reports & Analytics** (Reports App)

#### Reports Analyst (`reports_analyst`)
- Report generation
- Data analysis
- Insights and trends
- **Apps**: Reports ✅, All modules 📖

#### Statistician (`statistician`)
- Statistical analysis
- Research support
- Data modeling
- **Apps**: Reports ✅, All modules 📖

---

### 9. **Staff Management** (Staff Management App)

#### HR Manager (`hr_manager`)
- Staff recruitment
- Performance management
- HR policy implementation
- **Apps**: Staff Management ✅, Budget 📖, Reports 📖

#### HR Officer (`hr_officer`)
- Employee records
- Leave management
- Basic HR operations
- **Apps**: Staff Management ✅

---

### 10. **Budget & Financial Planning** (Budget App)

#### Budget Officer (`budget_officer`)
- Budget preparation
- Expense tracking
- Budget reports
- **Apps**: Budget ✅, Billing 📖, Reports 📖

#### Financial Controller (`financial_controller`)
- Financial control
- Budget approval
- Financial compliance
- **Apps**: Budget ✅, Billing ✅, Reports ✅

---

### 11. **Support & Maintenance**

#### IT Support (`it_support`)
- Technical support
- System maintenance
- User account management
- **Apps**: All modules 📖, System settings ✅

#### Maintenance Staff (`maintenance_staff`)
- Facility maintenance
- Equipment upkeep
- Basic support
- **Apps**: Limited access

---

## Permission Legend

- ✅ **Full Access**: Create, Read, Update, Delete
- 📖 **Read Only**: View information only
- ❌ **No Access**: Cannot access module

---

## Role Assignment Guidelines

### When to Assign Each Role:

1. **Clinical Roles**: Based on professional qualifications and licenses
2. **Administrative Roles**: Based on management responsibilities
3. **Support Roles**: Based on departmental functions
4. **Financial Roles**: Based on financial responsibilities and authority

### Multi-Role Users:
Some staff members may need multiple role capabilities. Consider:
- Small clinics: Combine related roles
- Large clinics: Assign specific, focused roles
- Always maintain principle of least privilege

---

## Default Role
**Default role for new users**: `receptionist`
- Basic access to patient registration and appointments
- Safest starting point for training new staff

---

## Migration Instructions

After updating roles in the system:

1. **Create Migration**:
   ```bash
   python manage.py makemigrations accounts
   ```

2. **Apply Migration**:
   ```bash
   python manage.py migrate accounts
   ```

3. **Update Existing Users**:
   - Review all existing user accounts
   - Reassign roles based on actual job functions
   - Update permissions as needed

4. **Test Access**:
   - Login with different role accounts
   - Verify appropriate access levels
   - Check that restrictions work correctly

---

## Security Best Practices

1. **Principle of Least Privilege**: Give users only the access they need
2. **Regular Review**: Audit user roles quarterly
3. **Role Changes**: Document all role changes
4. **Departure Process**: Immediately deactivate accounts when staff leave
5. **Strong Passwords**: Enforce password complexity requirements

---

## Total Roles in System: **29 Roles**

**By Category**:
- Administration & Management: 3 roles
- Clinical Staff: 5 roles
- Reception & Front Desk: 3 roles
- Laboratory: 3 roles
- Pharmacy: 3 roles
- Billing & Finance: 4 roles
- Medical Records: 3 roles
- Reports & Analytics: 2 roles
- Staff Management: 2 roles
- Budget & Financial Planning: 2 roles
- Support & Maintenance: 2 roles

---

## Quick Reference Table

| App Module | Primary Roles |
|------------|---------------|
| **Clinic Settings** | admin, clinic_manager |
| **Accounts** | admin, hr_manager |
| **Patients** | doctor, physiotherapist, nutritionist, nurse, receptionist |
| **Appointments** | receptionist, appointment_coordinator, clinical staff |
| **Billing** | billing_officer, accountant, finance_manager, cashier |
| **Medical Records** | medical_records_officer, records_manager, clinical staff |
| **Laboratory** | lab_technician, lab_manager, pathologist |
| **Pharmacy** | pharmacist, pharmacy_assistant, pharmacy_manager |
| **Reports** | reports_analyst, statistician, managers |
| **Staff Management** | hr_manager, hr_officer, clinic_manager |
| **Budget** | budget_officer, financial_controller, finance_manager |

---

## Contact & Support

For role assignment questions or access issues:
- Contact: System Administrator
- Email: admin@physioclinic.com
- Phone: +256 792 327 738

---

**Last Updated**: November 14, 2024  
**Document Version**: 1.0  
**Author**: PhysioNutrition Clinic IT Team
