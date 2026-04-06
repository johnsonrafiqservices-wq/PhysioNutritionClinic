# Modal Forms Implementation Guide
**PhysioNutrition Clinic Management System**

## Overview
This guide explains how to use the modal forms system implemented across the clinic management system. All data entry forms now use modal popups with AJAX submissions for a seamless user experience.

## Files Created

### JavaScript Library
- **`static/js/modal-forms.js`** - Reusable AJAX form handling library with validation and error display

### Modal Templates
- **`templates/modals/all_modals.html`** - Complete collection of all modal forms
- **`templates/modals/appointment_modals.html`** - Appointment-specific modals

## Installation & Setup

### 1. Include JavaScript Library in Base Template

Add to `templates/base.html` before closing `</body>` tag:

```html
<!-- Modal Forms Library -->
<script src="{% static 'js/modal-forms.js' %}"></script>
```

### 2. Include Modal Templates

Add to `templates/base.html` before closing `</body>` tag:

```html
<!-- All Modal Forms -->
{% include 'modals/all_modals.html' %}
```

## Available Modals

### Appointments
- **`appointmentCreateModal`** - Schedule new appointment
- **`appointmentRescheduleModal`** - Reschedule existing appointment
- **`treatmentSessionModal`** - Document treatment session

### Patients
- **`vitalSignsModal`** - Record vital signs

### Billing
- **`paymentRecordModal`** - Record payment

### Laboratory
- **`labRequestModal`** - Request lab test
- **`labResultModal`** - Record lab result

### Medical Records
- **`medicalRecordModal`** - Create medical record

### Inventory
- **`drugEntryModal`** - Add drug to inventory

## Usage Examples

### Opening a Modal from a Button

```html
<!-- Simple button to open modal -->
<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#appointmentCreateModal">
    <i class="bi bi-calendar-plus"></i> New Appointment
</button>

<!-- Button with JavaScript function (for dynamic data) -->
<button class="btn btn-danger" onclick="openVitalSignsModal('{{ patient.patient_id }}')">
    <i class="bi bi-heart-pulse"></i> Record Vitals
</button>
```

### Opening a Modal with JavaScript

```javascript
// Simple modal open
const modal = new bootstrap.Modal(document.getElementById('paymentRecordModal'));
modal.show();

// With dynamic data
function openPaymentModal(invoiceId) {
    const form = document.getElementById('paymentRecordForm');
    form.action = `/billing/ajax/payment/record/?invoice=${invoiceId}`;
    const modal = new bootstrap.Modal(document.getElementById('paymentRecordModal'));
    modal.show();
}
```

### Form Submission

Forms automatically submit via AJAX using the modal-forms library. No additional code needed:

```html
<form id="myForm" action="{% url 'app:ajax_endpoint' %}" method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>

<script>
document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
    window.modalForms.submitModalForm('myForm', 'myModal');
});
</script>
```

## Modal Forms Library API

### Core Functions

#### `submitModalForm(formId, modalId, onSuccess, onError)`
Submit a form via AJAX from within a modal.

```javascript
window.modalForms.submitModalForm('appointmentForm', 'appointmentModal', 
    function(data) {
        // Custom success handler
        console.log('Success:', data);
    },
    function(error) {
        // Custom error handler
        console.error('Error:', error);
    }
);
```

#### `showToast(message, type)`
Display toast notification.

```javascript
window.modalForms.showToast('Appointment created successfully!', 'success');
// Types: 'success', 'error', 'warning', 'info'
```

#### `clearValidationErrors(formId)`
Clear all validation errors from a form.

```javascript
window.modalForms.clearValidationErrors('appointmentForm');
```

#### `displayFormErrors(errors, formId)`
Display server-side validation errors.

```javascript
window.modalForms.displayFormErrors({
    'patient': ['This field is required'],
    'appointment_date': ['Invalid date']
}, 'appointmentForm');
```

#### `loadFormData(formId, data)`
Populate form fields with data.

```javascript
window.modalForms.loadFormData('appointmentForm', {
    'patient': '123',
    'appointment_date': '2025-10-24',
    'appointment_time': '10:00'
});
```

#### `setupModalReset(modalId, formId)`
Reset form when modal is closed.

```javascript
window.modalForms.setupModalReset('appointmentModal', 'appointmentForm');
```

#### `confirmAction(message, onConfirm, onCancel)`
Show simple confirmation dialog.

```javascript
window.modalForms.confirmAction(
    'Are you sure you want to delete this?',
    function() { /* delete action */ },
    function() { /* cancel action */ }
);
```

#### `showConfirmModal(title, message, onConfirm, options)`
Show Bootstrap confirmation modal.

```javascript
window.modalForms.showConfirmModal(
    'Delete Appointment',
    'Are you sure you want to delete this appointment?',
    function() {
        // Perform delete
    },
    {
        confirmText: 'Delete',
        cancelText: 'Cancel',
        confirmClass: 'btn-danger'
    }
);
```

## Creating New Modals

### Step 1: Create Modal HTML

```html
<div class="modal fade" id="myModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">My Modal Title</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <form id="myForm" action="{% url 'app:ajax_endpoint' %}" method="POST">
                {% csrf_token %}
                <div class="modal-body">
                    <!-- Form fields here -->
                    <div class="mb-3">
                        <label class="form-label">Field Name <span class="text-danger">*</span></label>
                        <input type="text" name="field_name" class="form-control" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </div>
            </form>
        </div>
    </div>
</div>
```

### Step 2: Add JavaScript Handler

```javascript
document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
    window.modalForms.submitModalForm('myForm', 'myModal');
});

// Setup reset
window.modalForms.setupModalReset('myModal', 'myForm');
```

### Step 3: Create AJAX View

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def my_ajax_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = MyForm(request.POST)
    if form.is_valid():
        instance = form.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Record created successfully!',
            'redirect_url': reverse('app:detail', kwargs={'pk': instance.pk})
        })
    else:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below.'
        }, status=400)
```

### Step 4: Add URL Pattern

```python
urlpatterns = [
    path('ajax/my-endpoint/', views.my_ajax_view, name='my_ajax_endpoint'),
]
```

## Modal Styling Guidelines

### Header Colors by Purpose

```html
<!-- Create/Add actions -->
<div class="modal-header bg-primary text-white">

<!-- Update/Edit actions -->
<div class="modal-header bg-warning text-dark">

<!-- Delete/Cancel actions -->
<div class="modal-header bg-danger text-white">

<!-- Info/View actions -->
<div class="modal-header bg-info text-white">

<!-- Success actions -->
<div class="modal-header bg-success text-white">
```

### Button Colors

```html
<!-- Primary action -->
<button class="btn btn-primary">Submit</button>

<!-- Secondary/Cancel action -->
<button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>

<!-- Danger/Delete action -->
<button class="btn btn-danger">Delete</button>

<!-- Success action -->
<button class="btn btn-success">Save</button>
```

## Best Practices

### 1. Always Use CSRF Token
```html
<form method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 2. Mark Required Fields
```html
<label class="form-label">Field Name <span class="text-danger">*</span></label>
<input type="text" name="field" class="form-control" required>
```

### 3. Use Bootstrap Icons
```html
<i class="bi bi-calendar-plus"></i> <!-- Bootstrap Icons -->
```

### 4. Implement Proper Validation
- Client-side: HTML5 required, pattern, min, max attributes
- Server-side: Django form validation
- Display errors: Use `displayFormErrors()` function

### 5. Handle Loading States
The library automatically disables submit buttons and shows loading state during AJAX requests.

### 6. Provide User Feedback
```javascript
// Success
window.modalForms.showToast('Operation completed successfully!', 'success');

// Error
window.modalForms.showToast('An error occurred. Please try again.', 'error');

// Warning
window.modalForms.showToast('Please review the information.', 'warning');

// Info
window.modalForms.showToast('Processing your request...', 'info');
```

## Troubleshooting

### Modal Doesn't Open
- Check if Bootstrap is loaded
- Verify modal ID matches data-bs-target
- Check browser console for JavaScript errors

### Form Doesn't Submit
- Verify form has ID attribute
- Check if AJAX endpoint URL is correct
- Ensure CSRF token is present
- Check browser console for errors

### Validation Errors Don't Display
- Verify field names match between frontend and backend
- Check server returns proper JSON error structure
- Ensure `displayFormErrors()` is called

### Modal Doesn't Close After Success
- Verify modal ID matches in JavaScript
- Check if Bootstrap Modal instance is being retrieved correctly
- Ensure success callback is returning proper data structure

## Complete Example: Create Appointment Modal

### Template (HTML)
```html
<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#appointmentModal">
    New Appointment
</button>

<div class="modal fade" id="appointmentModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Schedule Appointment</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <form id="appointmentForm" action="{% url 'appointments:create_ajax' %}" method="POST">
                {% csrf_token %}
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Patient <span class="text-danger">*</span></label>
                        <select name="patient" class="form-control" required>
                            <option value="">Select Patient</option>
                            {% for patient in patients %}
                            <option value="{{ patient.id }}">{{ patient.get_full_name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date <span class="text-danger">*</span></label>
                        <input type="date" name="appointment_date" class="form-control" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Schedule</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
document.getElementById('appointmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    window.modalForms.submitModalForm('appointmentForm', 'appointmentModal');
});
window.modalForms.setupModalReset('appointmentModal', 'appointmentForm');
</script>
```

### View (Python)
```python
@login_required
def appointment_create_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    form = AppointmentForm(request.POST)
    if form.is_valid():
        appointment = form.save()
        return JsonResponse({
            'success': True,
            'message': 'Appointment scheduled successfully!',
            'redirect_url': reverse('appointments:detail', kwargs={'pk': appointment.pk})
        })
    else:
        errors = {field: error_list for field, error_list in form.errors.items()}
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below.'
        }, status=400)
```

### URL (Python)
```python
urlpatterns = [
    path('ajax/create/', views.appointment_create_ajax, name='create_ajax'),
]
```

## Summary

The modal forms system provides:
- ✅ Seamless user experience without page reloads
- ✅ Real-time validation feedback
- ✅ Consistent error handling
- ✅ Reusable JavaScript library
- ✅ Professional UI/UX
- ✅ Easy to extend and maintain

For questions or issues, refer to the `MODAL_CONVERSION_PLAN.md` file or check the implementation examples in the codebase.
