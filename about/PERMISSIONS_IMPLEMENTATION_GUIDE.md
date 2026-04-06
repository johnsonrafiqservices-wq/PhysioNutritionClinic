# Permissions Implementation Guide
## PhysioNutrition Clinic Role-Based Access Control

This guide explains how to implement and use the role-based permissions system across all apps.

---

## Table of Contents
1. [Overview](#overview)
2. [Permission Matrix](#permission-matrix)
3. [Using Decorators in Views](#using-decorators-in-views)
4. [Template Permission Checks](#template-permission-checks)
5. [Implementation Examples](#implementation-examples)
6. [Testing Permissions](#testing-permissions)

---

## Overview

The permissions system controls access to resources based on user roles. Each role has:
- **Apps**: Which modules they can access
- **Permissions**: What actions they can perform (create, read, update, delete, admin)
- **Restricted Access**: Limited permissions to certain apps

### Permission Levels
- `create` - Can create new records
- `read` - Can view records
- `update` - Can modify existing records
- `delete` - Can delete records
- `admin` - Full administrative access

---

## Permission Matrix

### Role Access Summary

| Role | Primary Apps | Create | Read | Update | Delete |
|------|-------------|--------|------|--------|--------|
| **System Administrator** | All | ✅ | ✅ | ✅ | ✅ |
| **Clinic Manager** | All (except system) | ✅ | ✅ | ✅ | ✅ |
| **Doctor/GP** | Patients, Appointments, Records, Lab, Pharmacy | ✅ | ✅ | ✅ | ❌ |
| **Physiotherapist** | Patients, Appointments, Records | ✅ | ✅ | ✅ | ❌ |
| **Nutritionist** | Patients, Appointments, Records | ✅ | ✅ | ✅ | ❌ |
| **Receptionist** | Patients, Appointments | ✅ | ✅ | ✅ | ❌ |
| **Lab Technician** | Laboratory | ✅ | ✅ | ✅ | ❌ |
| **Pharmacist** | Pharmacy | ✅ | ✅ | ✅ | ✅ |
| **Billing Officer** | Billing | ✅ | ✅ | ✅ | ✅ |
| **Accountant** | Billing, Budget, Reports | ✅ | ✅ | ✅ | ✅ |

*See `SYSTEM_ROLES_GUIDE.md` for complete matrix*

---

## Using Decorators in Views

### 1. **App Access Required**
Restrict view to users with access to a specific app:

```python
from accounts.permissions import app_access_required

@app_access_required('patients')
def patient_list(request):
    # Only users with 'patients' app access can view this
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})
```

### 2. **Specific Permission Required**
Require specific permission for an action:

```python
from accounts.permissions import permission_required

@permission_required('patients', 'create')
def patient_register(request):
    # Only users who can CREATE in 'patients' app
    if request.method == 'POST':
        # ... create patient
        pass
    return render(request, 'patients/register.html')

@permission_required('billing', 'delete')
def delete_invoice(request, pk):
    # Only users who can DELETE in 'billing' app
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    return redirect('billing:invoice_list')
```

### 3. **Medical Staff Only**
Restrict to clinical staff:

```python
from accounts.permissions import medical_staff_required

@medical_staff_required
def create_assessment(request, patient_id):
    # Only doctors, nurses, physiotherapists, nutritionists
    patient = get_object_or_404(Patient, patient_id=patient_id)
    # ... assessment logic
    return render(request, 'patients/assessment.html')
```

### 4. **Admin or Manager Only**
Restrict to management:

```python
from accounts.permissions import admin_or_manager_required

@admin_or_manager_required
def clinic_settings(request):
    # Only admin, clinic_manager, medical_director
    # ... settings logic
    return render(request, 'settings/clinic.html')
```

### 5. **Department-Specific Access**

```python
from accounts.permissions import lab_staff_required, pharmacy_staff_required, finance_staff_required

@lab_staff_required
def add_lab_result(request):
    # Only lab staff can add results
    pass

@pharmacy_staff_required
def dispense_medication(request):
    # Only pharmacy staff can dispense
    pass

@finance_staff_required
def generate_financial_report(request):
    # Only finance staff can generate reports
    pass
```

---

## Template Permission Checks

### Load Permission Tags
```django
{% load permission_tags %}
```

### 1. **Check App Access**
```django
{% if user|has_app:'patients' %}
    <a href="{% url 'patients:patient_list' %}">View Patients</a>
{% endif %}

{% if user|has_app:'billing' %}
    <a href="{% url 'billing:invoice_list' %}">Billing</a>
{% endif %}
```

### 2. **Check Specific Permission**
```django
{% if user|can:'patients:create' %}
    <a href="{% url 'patients:patient_register' %}" class="btn btn-primary">
        Add New Patient
    </a>
{% endif %}

{% if user|can:'billing:delete' %}
    <button class="btn btn-danger" onclick="deleteInvoice()">Delete Invoice</button>
{% endif %}
```

### 3. **Use Simple Tags**
```django
{% user_can user 'patients' 'update' as can_update_patient %}
{% if can_update_patient %}
    <a href="{% url 'patients:edit' patient.id %}">Edit Patient</a>
{% endif %}

{% user_permissions_for user 'laboratory' as lab_perms %}
{% if 'create' in lab_perms %}
    <button class="btn btn-success">Add Lab Result</button>
{% endif %}
```

### 4. **Context Variables** (available in all templates)
```django
{% if is_medical_staff %}
    <!-- Show clinical features -->
    <a href="{% url 'patients:assessment' %}">Clinical Assessment</a>
{% endif %}

{% if is_admin_or_manager %}
    <!-- Show management features -->
    <a href="{% url 'reports:dashboard' %}">Management Dashboard</a>
{% endif %}

{% if is_finance_staff %}
    <!-- Show financial features -->
    <a href="{% url 'billing:financial_reports' %}">Financial Reports</a>
{% endif %}

{% if is_lab_staff %}
    <!-- Show lab features -->
    <a href="{% url 'laboratory:results' %}">Lab Results</a>
{% endif %}

{% if is_pharmacy_staff %}
    <!-- Show pharmacy features -->
    <a href="{% url 'pharmacy:dispensary' %}">Pharmacy Dispensary</a>
{% endif %}
```

### 5. **Menu Navigation Example**
```django
<nav class="sidebar">
    <ul>
        {% if user|has_app:'patients' %}
        <li>
            <a href="{% url 'patients:patient_list' %}">
                <i class="bi bi-people"></i> Patients
            </a>
        </li>
        {% endif %}
        
        {% if user|has_app:'appointments' %}
        <li>
            <a href="{% url 'appointments:list' %}">
                <i class="bi bi-calendar"></i> Appointments
            </a>
        </li>
        {% endif %}
        
        {% if user|has_app:'billing' %}
        <li>
            <a href="{% url 'billing:dashboard' %}">
                <i class="bi bi-cash"></i> Billing
            </a>
        </li>
        {% endif %}
        
        {% if user|has_app:'laboratory' %}
        <li>
            <a href="{% url 'laboratory:tests' %}">
                <i class="bi bi-flask"></i> Laboratory
            </a>
        </li>
        {% endif %}
    </ul>
</nav>
```

---

## Implementation Examples

### Example 1: Patient Management Views

```python
# patients/views.py
from django.contrib.auth.decorators import login_required
from accounts.permissions import app_access_required, permission_required, medical_staff_required

@app_access_required('patients')
def patient_list(request):
    """Anyone with patient app access can view list"""
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})

@permission_required('patients', 'create')
def patient_register(request):
    """Only users who can CREATE patients"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.save()
            return redirect('patients:detail', patient_id=patient.patient_id)
    else:
        form = PatientForm()
    return render(request, 'patients/register.html', {'form': form})

@medical_staff_required
def patient_assessment(request, patient_id):
    """Only medical staff can perform assessments"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    # Assessment logic
    return render(request, 'patients/assessment.html', {'patient': patient})

@permission_required('patients', 'delete')
def patient_delete(request, patient_id):
    """Only users with DELETE permission"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    patient.delete()
    messages.success(request, 'Patient record deleted successfully.')
    return redirect('patients:list')
```

### Example 2: Laboratory Views

```python
# laboratory/views.py
from accounts.permissions import lab_staff_required, permission_required

@lab_staff_required
def lab_dashboard(request):
    """Only lab staff can access lab dashboard"""
    pending_tests = LabTest.objects.filter(status='pending')
    return render(request, 'laboratory/dashboard.html', {
        'pending_tests': pending_tests
    })

@permission_required('laboratory', 'create')
def add_test_result(request, test_id):
    """Only those who can CREATE in lab"""
    test = get_object_or_404(LabTest, id=test_id)
    if request.method == 'POST':
        # Add result
        test.result = request.POST.get('result')
        test.status = 'completed'
        test.save()
        return redirect('laboratory:dashboard')
    return render(request, 'laboratory/add_result.html', {'test': test})
```

### Example 3: Billing Views

```python
# billing/views.py
from accounts.permissions import finance_staff_required, permission_required

@finance_staff_required
def billing_dashboard(request):
    """Only finance staff"""
    invoices = Invoice.objects.all()
    return render(request, 'billing/dashboard.html', {'invoices': invoices})

@permission_required('billing', 'create')
def create_invoice(request):
    """Only those who can CREATE invoices"""
    # Invoice creation logic
    pass

@permission_required('billing', 'delete')
def delete_payment(request, payment_id):
    """Only those who can DELETE payments"""
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    return redirect('billing:dashboard')
```

---

## Checking Permissions Programmatically

### In Views
```python
from accounts.permissions import has_permission, get_user_permissions

def my_view(request):
    user = request.user
    
    # Check single permission
    if has_permission(user, 'patients', 'create'):
        # User can create patients
        pass
    
    # Get all permissions for an app
    billing_perms = get_user_permissions(user, 'billing')
    # billing_perms might be ['read', 'create', 'update']
    
    if 'delete' in billing_perms:
        # User can delete in billing
        pass
```

### In Python Shell
```python
from django.contrib.auth import get_user_model
from accounts.permissions import has_app_access, has_permission

User = get_user_model()
user = User.objects.get(username='john_doe')

# Check app access
has_app_access(user, 'patients')  # True/False

# Check specific permission
has_permission(user, 'billing', 'create')  # True/False

# Check role
if user.role == 'doctor':
    print("This user is a doctor")
```

---

## Testing Permissions

### Test User Creation
```python
# Create test users with different roles
from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin
admin = User.objects.create_user(
    username='admin',
    password='test123',
    role='admin',
    first_name='Admin',
    last_name='User'
)

# Create doctor
doctor = User.objects.create_user(
    username='doctor',
    password='test123',
    role='doctor',
    first_name='Dr. John',
    last_name='Smith'
)

# Create receptionist
receptionist = User.objects.create_user(
    username='receptionist',
    password='test123',
    role='receptionist',
    first_name='Jane',
    last_name='Doe'
)
```

### Manual Testing Steps
1. **Login as different roles**
   - Test admin access (should see everything)
   - Test doctor access (should see clinical modules)
   - Test receptionist access (should see limited features)

2. **Try restricted actions**
   - Login as receptionist
   - Try to access billing dashboard
   - Should be redirected with error message

3. **Verify menu visibility**
   - Check sidebar navigation
   - Only relevant apps should appear

4. **Test CRUD operations**
   - Create: Try to add new records
   - Read: Try to view lists
   - Update: Try to edit records
   - Delete: Try to delete records

---

## Common Patterns

### Pattern 1: Conditional Form Fields
```python
def patient_form(request):
    if has_permission(request.user, 'patients', 'update'):
        # Show all fields
        form = PatientForm()
    else:
        # Show read-only fields
        form = PatientForm()
        for field in form.fields:
            form.fields[field].disabled = True
    return render(request, 'form.html', {'form': form})
```

### Pattern 2: Filtered Querysets
```python
def invoice_list(request):
    if request.user.role == 'cashier':
        # Cashiers only see today's invoices
        invoices = Invoice.objects.filter(created_at__date=today())
    elif request.user.role == 'finance_manager':
        # Managers see all invoices
        invoices = Invoice.objects.all()
    else:
        # Others see limited view
        invoices = Invoice.objects.filter(status='paid')
    return render(request, 'invoices.html', {'invoices': invoices})
```

### Pattern 3: Action Buttons
```django
<div class="btn-group">
    {% if user|can:'patients:read' %}
        <a href="{% url 'patients:detail' patient.id %}" class="btn btn-primary">
            <i class="bi bi-eye"></i> View
        </a>
    {% endif %}
    
    {% if user|can:'patients:update' %}
        <a href="{% url 'patients:edit' patient.id %}" class="btn btn-warning">
            <i class="bi bi-pencil"></i> Edit
        </a>
    {% endif %}
    
    {% if user|can:'patients:delete' %}
        <button onclick="deletePatient({{ patient.id }})" class="btn btn-danger">
            <i class="bi bi-trash"></i> Delete
        </button>
    {% endif %}
</div>
```

---

## Troubleshooting

### Issue: User can't access anything
**Solution**: Check that:
1. User has a valid role assigned
2. Role is in ROLE_PERMISSIONS dictionary
3. User is active (`is_active=True`)

### Issue: Permission denied even with correct role
**Solution**: Check:
1. App name matches exactly (e.g., 'patients' not 'patient')
2. Permission name is correct ('create', 'read', 'update', 'delete')
3. Context processor is added to settings

### Issue: Template tags not working
**Solution**: Ensure:
1. `{% load permission_tags %}` at top of template
2. `accounts.permissions.user_permissions` in context processors
3. Server restarted after adding template tags

---

## Best Practices

1. **Always use decorators on views** - Don't rely only on template hiding
2. **Validate in both template and view** - Defense in depth
3. **Use specific permissions** - Prefer `permission_required` over generic checks
4. **Test with multiple roles** - Always test new features with different user roles
5. **Document custom permissions** - If you add new permissions, document them
6. **Audit regularly** - Review user roles and permissions quarterly
7. **Follow least privilege** - Give users only the access they need

---

## Quick Reference Card

```python
# View Decorators
@app_access_required('patients')          # Has access to app
@permission_required('patients', 'create') # Can create in app
@medical_staff_required                    # Is medical staff
@admin_or_manager_required                 # Is admin/manager
@finance_staff_required                    # Is finance staff
@lab_staff_required                        # Is lab staff
@pharmacy_staff_required                   # Is pharmacy staff

# Template Checks
{% if user|has_app:'patients' %}          # Has app access
{% if user|can:'patients:create' %}       # Has permission
{% if is_medical_staff %}                 # Is medical staff
{% if is_admin_or_manager %}              # Is admin/manager
{% if is_finance_staff %}                 # Is finance staff

# Python Functions
has_app_access(user, 'patients')          # Returns True/False
has_permission(user, 'patients', 'create') # Returns True/False
get_user_apps(user)                       # Returns list of apps
get_user_permissions(user, 'patients')     # Returns list of permissions
```

---

**Last Updated**: November 14, 2024  
**Version**: 1.0  
**Author**: PhysioNutrition Clinic IT Team
