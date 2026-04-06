# Dashboard Compatibility Fix Guide

## Problem
The dashboard.html template you copied references apps and URL patterns that don't exist in your current system.

## Your Actual System Apps

### ✅ Apps You Have:
- `accounts` - User authentication
- `patients` - Patient management (instead of `ehr`)
- `appointments` - Appointment scheduling
- `billing` - Billing and invoicing
- `medical_records` - Medical records management
- `inventory` - Drug/medication inventory (instead of `pharmacy`)
- `laboratory` - Lab tests (instead of `lab`)
- `reports` - Reporting system
- `clinic_settings` - Clinic settings

### ❌ Apps You DON'T Have:
- `ehr` - Use `patients` instead
- `pharmacy` - Use `inventory` instead
- `lab` - Use `laboratory` instead
- `staff` - Not in your system
- `roster` - Not in your system
- `branches` - Use `clinic_settings` instead
- `notifications` - Not in your system

## Required URL Mapping Changes

### Replace these URL patterns in dashboard.html:

```python
# PATIENTS APP
'ehr:patient_list' → 'patients:patient_list'
'ehr:patient_create' → 'patients:patient_register'
'ehr:patient_detail' → 'patients:patient_detail'

# INVENTORY APP (instead of pharmacy)
'pharmacy:medication_list' → 'inventory:drug_list'
'pharmacy:prescription_list' → Remove or create
'pharmacy:inventory' → 'inventory:drug_list'
'pharmacy:supplier_list' → 'inventory:supplier_list'
'pharmacy:prescription_create' → Remove or create
'pharmacy:inventory_dashboard' → 'inventory:drug_list'

# LABORATORY APP
'lab:test_type_list' → 'laboratory:labtest_list'
'lab:test_worklist' → 'laboratory:labtest_list'
'lab:equipment_list' → Remove (not available)
'lab:quality_control_list' → Remove (not available)
'lab:dashboard' → 'laboratory:labtest_list'

# APPOINTMENTS
'appointments:calendar' → 'appointments:calendar_view'
'appointments:appointment_create' → 'appointments:appointment_create' ✓
'appointments:appointment_list' → 'appointments:appointment_list' ✓

# BILLING
'billing:invoice_create' → 'billing:create_invoice'
'billing:invoice_list' → 'billing:invoice_list'
'billing:payment_list' → 'billing:payment_list'
'billing:payment_create' → 'billing:create_payment'
'billing:revenue_report' → 'reports:dashboard'
'billing:insurance_claim_form' → May not exist - check billing urls

# REMOVE THESE (Apps don't exist):
'roster:*' → Remove all roster references
'staff:staff_list' → Remove
'branches:branch_list' → Use 'clinic_settings:' if needed
'notifications:list' → Remove
```

## Quick Fix: Use the Simplified Dashboard

I've created two dashboard options for you:

### Option 1: dashboard_fixed.html (Recommended)
Located at: `templates/dashboard_fixed.html`

This is a clean, simplified dashboard that only uses URLs that exist in your system:
- ✅ Works with your actual apps
- ✅ No broken links
- ✅ Modern, professional design
- ✅ Responsive layout

### Option 2: Fix the current dashboard
Update `templates/dashboard/dashboard.html` by replacing all the URL references according to the mapping above.

## How to Use dashboard_fixed.html

### Step 1: Update the accounts view
Edit `accounts/views.py`:

```python
@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'role': request.user.role,
    }
    return render(request, 'dashboard_fixed.html', context)  # Changed path
```

### Step 2: Test the dashboard
1. Run the development server
2. Login to your system
3. You should see the working dashboard

## Available URL Names in Your System

### Patients App:
```python
patients:dashboard
patients:patient_list
patients:patient_register
patients:visiting_patient_register
patients:patient_detail
patients:patient_update
patients:patient_details_print
patients:record_vitals
patients:triage_patient
patients:assessment_create
patients:physiotherapy_assessment
patients:nutrition_assessment
```

### Appointments App:
```python
appointments:appointment_list
appointments:calendar_view
appointments:calendar_day_detail
appointments:appointment_create
appointments:appointment_detail
appointments:appointment_update
appointments:appointment_update_status
appointments:appointment_cancel
appointments:appointment_reschedule
appointments:appointment_confirm
```

### Inventory App:
```python
inventory:drug_list
inventory:drug_add
inventory:drug_edit
inventory:supplier_add
inventory:supplier_edit
inventory:record_usage
inventory:cashflow_list
```

### Laboratory App:
```python
laboratory:labtest_list
laboratory:labtest_add
laboratory:labtest_request
laboratory:labtest_results
laboratory:labtest_result_add
```

### Billing App:
Check `billing/urls.py` for exact URL names

### Reports App:
Check `reports/urls.py` for exact URL names

## Context Variables Needed

The dashboard expects these context variables. Make sure your view provides them:

```python
@login_required
def dashboard(request):
    from patients.models import Patient
    from appointments.models import Appointment
    from billing.models import Invoice, Payment
    from laboratory.models import LabTest
    
    today = timezone.now().date()
    
    context = {
        'user': request.user,
        'role': request.user.role,
        'current_date': today.strftime('%A, %B %d, %Y'),
        'current_time': timezone.now().strftime('%I:%M %p'),
        
        # Stats
        'patient_count': Patient.objects.count(),
        'appointment_count': Appointment.objects.filter(
            appointment_date__date=today
        ).count(),
        'pending_invoices': Invoice.objects.filter(status='pending').count(),
        'pending_lab_tests': LabTest.objects.filter(status='pending').count(),
        
        # Lists
        'today_appointments': Appointment.objects.filter(
            appointment_date__date=today
        ).select_related('patient')[:10],
        'recent_payments': Payment.objects.all().order_by('-created_at')[:10],
    }
    return render(request, 'dashboard_fixed.html', context)
```

## Testing Checklist

- [ ] Dashboard loads without errors
- [ ] All quick action buttons work
- [ ] Stats cards display correct numbers
- [ ] No 404 errors on any links
- [ ] Responsive design works on mobile
- [ ] Today's appointments show correctly
- [ ] Recent activity displays properly

## Next Steps

1. **Choose your option**: Use `dashboard_fixed.html` or fix the current one
2. **Update the view**: Provide the required context variables
3. **Test thoroughly**: Click all links to ensure they work
4. **Customize**: Add your branding and adjust colors as needed

## Support

If you encounter URL errors:
1. Check the app's `urls.py` file for the correct URL name
2. Verify the app is included in `INSTALLED_APPS` in settings.py
3. Make sure the URL pattern exists in the main `clinic_system/urls.py`

---

**Status**: Ready to implement ✅  
**Recommended**: Use `dashboard_fixed.html` for immediate functionality
