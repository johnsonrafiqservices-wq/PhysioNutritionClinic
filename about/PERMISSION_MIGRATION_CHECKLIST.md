# Permission Migration Checklist
## Steps to Apply Role-Based Permissions to Existing Views

This checklist helps you systematically add permissions to all views in your system.

---

## Phase 1: Setup ✅

- [x] Create `accounts/permissions.py`
- [x] Add `user_permissions` context processor to settings
- [x] Create `accounts/templatetags/permission_tags.py`
- [x] Create `templatetags/__init__.py`
- [ ] Run migration: `python manage.py migrate accounts`
- [ ] Restart Django server

---

## Phase 2: Update Views by App

### Patients App

#### Views to Update:
```python
# patients/views.py

# Current views that need decorators:
- [ ] patient_list → @app_access_required('patients')
- [ ] patient_detail → @app_access_required('patients')
- [ ] patient_register → @permission_required('patients', 'create')
- [ ] patient_update → @permission_required('patients', 'update')
- [ ] patient_delete → @permission_required('patients', 'delete')
- [ ] vital_signs_record → @medical_staff_required
- [ ] physiotherapy_assessment → @medical_staff_required
- [ ] nutrition_assessment → @medical_staff_required
- [ ] general_assessment → @medical_staff_required
- [ ] triage_create → @medical_staff_required
```

**Example Implementation:**
```python
from accounts.permissions import (
    app_access_required, 
    permission_required, 
    medical_staff_required
)

@app_access_required('patients')
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})

@permission_required('patients', 'create')
def patient_register(request):
    # Registration logic
    pass

@medical_staff_required
def physiotherapy_assessment(request, patient_id):
    # Assessment logic
    pass
```

---

### Appointments App

#### Views to Update:
```python
# appointments/views.py

- [ ] appointment_list → @app_access_required('appointments')
- [ ] appointment_detail → @app_access_required('appointments')
- [ ] appointment_create → @permission_required('appointments', 'create')
- [ ] appointment_update → @permission_required('appointments', 'update')
- [ ] appointment_cancel → @permission_required('appointments', 'delete')
- [ ] treatment_session → @medical_staff_required
- [ ] nutrition_consultation → @medical_staff_required
```

---

### Billing App

#### Views to Update:
```python
# billing/views.py

- [ ] billing_dashboard → @finance_staff_required
- [ ] invoice_list → @app_access_required('billing')
- [ ] invoice_detail → @app_access_required('billing')
- [ ] invoice_create → @permission_required('billing', 'create')
- [ ] invoice_update → @permission_required('billing', 'update')
- [ ] invoice_delete → @permission_required('billing', 'delete')
- [ ] payment_create → @permission_required('billing', 'create')
- [ ] payment_list → @finance_staff_required
- [ ] financial_reports → @finance_staff_required
```

---

### Laboratory App

#### Views to Update:
```python
# laboratory/views.py

- [ ] lab_dashboard → @lab_staff_required
- [ ] test_list → @app_access_required('laboratory')
- [ ] test_detail → @app_access_required('laboratory')
- [ ] test_create → @permission_required('laboratory', 'create')
- [ ] result_add → @lab_staff_required
- [ ] result_approve → @lab_staff_required (pathologist approval)
- [ ] result_detail → @app_access_required('laboratory')
```

---

### Pharmacy App

#### Views to Update:
```python
# pharmacy/views.py

- [ ] pharmacy_dashboard → @pharmacy_staff_required
- [ ] prescription_list → @app_access_required('pharmacy')
- [ ] dispense_medication → @pharmacy_staff_required
- [ ] drug_inventory → @permission_required('pharmacy', 'read')
- [ ] drug_add → @permission_required('pharmacy', 'create')
- [ ] drug_update → @permission_required('pharmacy', 'update')
```

---

### Medical Records App

#### Views to Update:
```python
# medical_records/views.py

- [ ] records_list → @app_access_required('medical_records')
- [ ] record_detail → @app_access_required('medical_records')
- [ ] record_create → @permission_required('medical_records', 'create')
- [ ] record_update → @permission_required('medical_records', 'update')
- [ ] record_archive → @permission_required('medical_records', 'delete')
```

---

### Reports App

#### Views to Update:
```python
# reports/views.py

- [ ] reports_dashboard → @app_access_required('reports')
- [ ] financial_report → @finance_staff_required
- [ ] clinical_report → @medical_staff_required
- [ ] statistical_analysis → @app_access_required('reports')
```

---

### Staff Management App

#### Views to Update:
```python
# staff_management/views.py

- [ ] staff_list → @app_access_required('staff_management')
- [ ] staff_detail → @app_access_required('staff_management')
- [ ] staff_create → @permission_required('staff_management', 'create')
- [ ] staff_update → @permission_required('staff_management', 'update')
- [ ] attendance_track → @app_access_required('staff_management')
```

---

### Budget App

#### Views to Update:
```python
# budget/views.py

- [ ] budget_dashboard → @app_access_required('budget')
- [ ] budget_create → @permission_required('budget', 'create')
- [ ] budget_update → @permission_required('budget', 'update')
- [ ] expense_track → @permission_required('budget', 'read')
```

---

## Phase 3: Update Templates

### Base Navigation (templates/base.html)

```django
{% load permission_tags %}

<!-- Sidebar Navigation -->
<nav class="sidebar">
    {% if user|has_app:'patients' %}
    <a href="{% url 'patients:patient_list' %}">
        <i class="bi bi-people"></i> Patients
    </a>
    {% endif %}
    
    {% if user|has_app:'appointments' %}
    <a href="{% url 'appointments:list' %}">
        <i class="bi bi-calendar"></i> Appointments
    </a>
    {% endif %}
    
    {% if user|has_app:'billing' %}
    <a href="{% url 'billing:dashboard' %}">
        <i class="bi bi-cash"></i> Billing
    </a>
    {% endif %}
    
    {% if user|has_app:'laboratory' %}
    <a href="{% url 'laboratory:tests' %}">
        <i class="bi bi-flask"></i> Laboratory
    </a>
    {% endif %}
    
    {% if user|has_app:'pharmacy' %}
    <a href="{% url 'pharmacy:dashboard' %}">
        <i class="bi bi-capsule"></i> Pharmacy
    </a>
    {% endif %}
    
    {% if user|has_app:'medical_records' %}
    <a href="{% url 'medical_records:list' %}">
        <i class="bi bi-folder"></i> Records
    </a>
    {% endif %}
    
    {% if user|has_app:'reports' %}
    <a href="{% url 'reports:dashboard' %}">
        <i class="bi bi-graph-up"></i> Reports
    </a>
    {% endif %}
    
    {% if user|has_app:'staff_management' %}
    <a href="{% url 'staff_management:list' %}">
        <i class="bi bi-person-badge"></i> Staff
    </a>
    {% endif %}
    
    {% if user|has_app:'budget' %}
    <a href="{% url 'budget:dashboard' %}">
        <i class="bi bi-wallet"></i> Budget
    </a>
    {% endif %}
    
    {% if is_admin_or_manager %}
    <a href="{% url 'clinic_settings:settings' %}">
        <i class="bi bi-gear"></i> Settings
    </a>
    {% endif %}
</nav>
```

### Template Checklist:

- [ ] Update base.html navigation
- [ ] Update dashboard.html widgets based on role
- [ ] Update patient_list.html action buttons
- [ ] Update appointment_list.html action buttons
- [ ] Update invoice_list.html action buttons
- [ ] Update lab_results.html action buttons
- [ ] Update all forms with permission checks

---

## Phase 4: Testing

### Test Each Role:

#### Admin Role
- [ ] Can access all modules
- [ ] Can perform all CRUD operations
- [ ] Can access settings

#### Doctor Role
- [ ] Can access patients, appointments, medical records, lab, pharmacy
- [ ] Can create assessments
- [ ] Can write prescriptions
- [ ] Cannot access billing (except read)

#### Receptionist Role
- [ ] Can access patients and appointments
- [ ] Can register patients
- [ ] Can schedule appointments
- [ ] Cannot access clinical assessments
- [ ] Limited billing access (view only)

#### Lab Technician Role
- [ ] Can access laboratory module
- [ ] Can add test results
- [ ] Can view patient info (read-only)
- [ ] Cannot access other modules

#### Pharmacist Role
- [ ] Can access pharmacy module
- [ ] Can dispense medications
- [ ] Can view prescriptions
- [ ] Can manage inventory

#### Billing Officer Role
- [ ] Can access billing module
- [ ] Can create invoices
- [ ] Can record payments
- [ ] Can view patient info (read-only)

---

## Phase 5: Documentation

- [ ] Update user manual with role descriptions
- [ ] Create role assignment SOP
- [ ] Train staff on new permission system
- [ ] Document any custom permissions added

---

## Verification Commands

### Test Permissions in Shell
```python
python manage.py shell

from django.contrib.auth import get_user_model
from accounts.permissions import has_app_access, has_permission

User = get_user_model()

# Test doctor permissions
doctor = User.objects.get(role='doctor')
print(has_app_access(doctor, 'patients'))  # Should be True
print(has_permission(doctor, 'patients', 'create'))  # Should be True
print(has_app_access(doctor, 'budget'))  # Should be False

# Test receptionist permissions
receptionist = User.objects.get(role='receptionist')
print(has_app_access(receptionist, 'appointments'))  # Should be True
print(has_permission(receptionist, 'billing', 'delete'))  # Should be False
```

---

## Common Issues & Solutions

### Issue 1: Import Error
```
ImportError: cannot import name 'app_access_required'
```
**Solution**: Ensure you've restarted the Django server after creating permissions.py

### Issue 2: Context Variables Not Available
```
TemplateSyntaxError: 'is_medical_staff' is undefined
```
**Solution**: Check that `accounts.permissions.user_permissions` is in TEMPLATES context_processors

### Issue 3: Permission Denied for Admin
```
Admin user getting "Permission denied" message
```
**Solution**: Ensure admin user has role='admin' or is_superuser=True

---

## Rollback Plan

If issues occur, you can temporarily disable permissions:

1. **Remove decorators** from views
2. **Comment out** context processor in settings
3. **Fix issues** and re-enable gradually

---

## Progress Tracking

| App | Views Updated | Templates Updated | Tested | Complete |
|-----|---------------|-------------------|--------|----------|
| Patients | ⬜ | ⬜ | ⬜ | ⬜ |
| Appointments | ⬜ | ⬜ | ⬜ | ⬜ |
| Billing | ⬜ | ⬜ | ⬜ | ⬜ |
| Laboratory | ⬜ | ⬜ | ⬜ | ⬜ |
| Pharmacy | ⬜ | ⬜ | ⬜ | ⬜ |
| Medical Records | ⬜ | ⬜ | ⬜ | ⬜ |
| Reports | ⬜ | ⬜ | ⬜ | ⬜ |
| Staff Management | ⬜ | ⬜ | ⬜ | ⬜ |
| Budget | ⬜ | ⬜ | ⬜ | ⬜ |

**Overall Progress**: 0% Complete

---

**Estimated Time**: 2-3 days for full implementation  
**Priority**: High - Security critical  
**Assigned To**: Development Team  
**Target Completion**: [Set Date]

---

**Last Updated**: November 14, 2024  
**Version**: 1.0  
**Status**: Ready for Implementation
