# Complete System Data Population Guide

## Overview
This guide will help you populate ALL models in the Excellence Medical Care system with 50 records each.

## Quick Start - Run All Commands

```bash
# 1. Users & Staff
python manage.py populate_users

# 2. Patients
python manage.py populate_patients

# 3. Appointments & Services
python manage.py populate_appointments

# 4. Assessments
python manage.py populate_assessments

# 5. Vital Signs
python manage.py populate_vitals

# 6. Pharmacy (Already Done)
python manage.py populate_medications
python manage.py populate_prescriptions

# 7. Laboratory
python manage.py populate_lab_tests
python manage.py populate_lab_requests

# 8. Billing
python manage.py populate_invoices

# 9. Medical Records
python manage.py populate_medical_records

# 10. Inventory
python manage.py populate_inventory

# 11. Budget
python manage.py populate_budget

# 12. Staff Management
python manage.py populate_staff_records
```

## Status of Existing Data

### ✅ Already Populated
- **Pharmacy**: 21 medications, 44 batches
- **Prescriptions**: 10 sample prescriptions

### 🔄 To Be Created
The following management commands need to be created and run.

##Human: there is no need for the above steps. jsut run the python manage.py populate_sample_data
