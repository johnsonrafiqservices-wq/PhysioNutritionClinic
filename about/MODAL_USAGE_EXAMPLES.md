# Modal Forms - Usage Examples
**PhysioNutrition Clinic Management System**

## Quick Reference for Using Modals

### Payment Recording Modal

**Function:** `openPaymentModal(invoiceId, invoiceNumber, balanceDue, patientId)`

**Example Usage:**

```html
<!-- From invoice detail page -->
<button class="btn btn-success" 
        onclick="openPaymentModal('{{ invoice.id }}', '{{ invoice.invoice_number }}', '{{ invoice.get_balance_due }}', '{{ invoice.patient.id }}')">
    <i class="bi bi-cash-coin"></i> Record Payment
</button>

<!-- From invoice list -->
{% for invoice in invoices %}
<button class="btn btn-sm btn-success" 
        onclick="openPaymentModal('{{ invoice.id }}', '{{ invoice.invoice_number }}', '{{ invoice.get_balance_due }}', '{{ invoice.patient.id }}')">
    Record Payment
</button>
{% endfor %}

<!-- Simple payment without invoice -->
<button class="btn btn-success" onclick="openPaymentModal()">
    Record Payment
</button>
```

**What it does:**
- Opens payment modal
- Pre-fills invoice ID and patient ID
- Sets amount to balance due
- Shows invoice information banner
- Submits via AJAX to `/billing/ajax/payment/record/`

---

### Appointment Scheduling Modal

**Function:** `openAppointmentModal(patientId)`

**Example Usage:**

```html
<!-- From patient detail page -->
<button class="btn btn-primary" 
        onclick="openAppointmentModal('{{ patient.id }}')">
    <i class="bi bi-calendar-plus"></i> Schedule Appointment
</button>

<!-- From dashboard or appointment list -->
<button class="btn btn-primary" onclick="openAppointmentModal()">
    <i class="bi bi-calendar-plus"></i> New Appointment
</button>

<!-- From patient list -->
{% for patient in patients %}
<button class="btn btn-sm btn-primary" 
        onclick="openAppointmentModal('{{ patient.id }}')">
    Schedule
</button>
{% endfor %}
```

**What it does:**
- Opens appointment creation modal
- Pre-selects patient if ID provided
- Sets date to today by default
- Submits via AJAX to `/appointments/ajax/create/`

**Required Context Variables:**
Add to your view context:
```python
context = {
    'all_patients': Patient.objects.filter(is_active=True).order_by('first_name'),
    'all_services': Service.objects.all(),
    'all_providers': User.objects.filter(is_active=True, role__in=['doctor', 'physiotherapist', 'nutritionist']),
}
```

---

### Vital Signs Modal

**Function:** `openVitalSignsModal(patientId)`

**Example Usage:**

```html
<!-- From patient detail page -->
<button class="btn btn-danger" 
        onclick="openVitalSignsModal('{{ patient.patient_id }}')">
    <i class="bi bi-heart-pulse"></i> Record Vitals
</button>

<!-- From patient list -->
{% for patient in patients %}
<button class="btn btn-sm btn-danger" 
        onclick="openVitalSignsModal('{{ patient.patient_id }}')">
    Vitals
</button>
{% endfor %}
```

**What it does:**
- Opens vital signs modal
- Sets form action with patient ID
- Submits via AJAX to `/patients/ajax/{patient_id}/vitals/`

---

## Complete Button Examples

### Patient Detail Page - Quick Actions

```html
<div class="card mb-3">
    <div class="card-header">
        <h5><i class="bi bi-lightning-fill"></i> Quick Actions</h5>
    </div>
    <div class="card-body">
        <div class="d-grid gap-2">
            <!-- Schedule Appointment -->
            <button class="btn btn-primary" 
                    onclick="openAppointmentModal('{{ patient.id }}')">
                <i class="bi bi-calendar-plus"></i> Schedule Appointment
            </button>
            
            <!-- Record Vitals -->
            <button class="btn btn-danger" 
                    onclick="openVitalSignsModal('{{ patient.patient_id }}')">
                <i class="bi bi-heart-pulse"></i> Record Vital Signs
            </button>
            
            <!-- Record Payment (if has unpaid invoices) -->
            {% if patient.invoices.filter(status__in=['sent', 'overdue']).exists %}
            {% with latest_invoice=patient.invoices.filter(status__in=['sent', 'overdue']).first %}
            <button class="btn btn-success" 
                    onclick="openPaymentModal('{{ latest_invoice.id }}', '{{ latest_invoice.invoice_number }}', '{{ latest_invoice.get_balance_due }}', '{{ patient.id }}')">
                <i class="bi bi-cash-coin"></i> Record Payment
            </button>
            {% endwith %}
            {% endif %}
        </div>
    </div>
</div>
```

### Invoice Detail Page - Action Buttons

```html
<div class="card-footer">
    <div class="btn-group" role="group">
        {% if invoice.status != 'paid' %}
        <button class="btn btn-success" 
                onclick="openPaymentModal('{{ invoice.id }}', '{{ invoice.invoice_number }}', '{{ invoice.get_balance_due }}', '{{ invoice.patient.id }}')">
            <i class="bi bi-cash-coin"></i> Record Payment
        </button>
        {% endif %}
        
        <a href="{% url 'billing:invoice_pdf' invoice.pk %}" class="btn btn-primary" target="_blank">
            <i class="bi bi-file-pdf"></i> View PDF
        </a>
        
        {% if invoice.status == 'draft' %}
        <a href="{% url 'billing:invoice_edit' invoice.pk %}" class="btn btn-warning">
            <i class="bi bi-pencil"></i> Edit Invoice
        </a>
        {% endif %}
    </div>
</div>
```

### Invoice List - Table Actions

```html
<table class="table">
    <thead>
        <tr>
            <th>Invoice #</th>
            <th>Patient</th>
            <th>Amount</th>
            <th>Balance</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for invoice in invoices %}
        <tr>
            <td>{{ invoice.invoice_number }}</td>
            <td>{{ invoice.patient.get_full_name }}</td>
            <td>UGX {{ invoice.total_amount|floatformat:0 }}</td>
            <td>UGX {{ invoice.get_balance_due|floatformat:0 }}</td>
            <td>
                <span class="badge bg-{{ invoice.get_status_color }}">
                    {{ invoice.get_status_display }}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <a href="{% url 'billing:invoice_detail' invoice.pk %}" class="btn btn-info">
                        <i class="bi bi-eye"></i>
                    </a>
                    
                    {% if invoice.status != 'paid' and invoice.get_balance_due > 0 %}
                    <button class="btn btn-success" 
                            onclick="openPaymentModal('{{ invoice.id }}', '{{ invoice.invoice_number }}', '{{ invoice.get_balance_due }}', '{{ invoice.patient.id }}')">
                        <i class="bi bi-cash"></i>
                    </button>
                    {% endif %}
                </div>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Appointment List - Quick Schedule

```html
<div class="card-header">
    <div class="d-flex justify-content-between align-items-center">
        <h5><i class="bi bi-calendar-check"></i> Appointments</h5>
        <button class="btn btn-primary btn-sm" onclick="openAppointmentModal()">
            <i class="bi bi-plus-circle"></i> New Appointment
        </button>
    </div>
</div>
```

---

## Adding Modals to Your Templates

### Step 1: Include the Modal Library

Add to your base template before `</body>`:

```html
<!-- Modal Forms Library -->
<script src="{% static 'js/modal-forms.js' %}"></script>

<!-- All Modal Forms -->
{% include 'modals/all_modals.html' %}
```

### Step 2: Add Context Variables

For pages using appointment modal, add to view:

```python
def my_view(request):
    # ... your code ...
    
    context = {
        # Your existing context
        'all_patients': Patient.objects.filter(is_active=True).order_by('first_name'),
        'all_services': Service.objects.all(),
        'all_providers': User.objects.filter(
            is_active=True, 
            role__in=['doctor', 'physiotherapist', 'nutritionist']
        ).order_by('first_name'),
    }
    return render(request, 'my_template.html', context)
```

### Step 3: Use the Buttons

Just add the onclick handlers as shown in examples above!

---

## Testing the Modals

### Test Payment Modal

1. Go to any invoice detail page
2. Click "Record Payment" button
3. Modal should open with invoice info pre-filled
4. Fill in payment method
5. Click "Record Payment"
6. Should show success message and close modal

### Test Appointment Modal

1. Go to patient detail page
2. Click "Schedule Appointment"
3. Modal should open with patient pre-selected
4. Select service, provider, date, and time
5. Click "Schedule"
6. Should show success message and close modal

### Test Vital Signs Modal

1. Go to patient detail page
2. Click "Record Vitals"
3. Modal should open
4. Enter vital signs
5. Click "Save Vital Signs"
6. Should show success message and close modal

---

## Troubleshooting

### Modal doesn't open
- Check if `all_modals.html` is included in base template
- Check if `modal-forms.js` is loaded
- Check browser console for JavaScript errors

### Payment modal shows blank amount
- Verify invoice balance is calculated correctly
- Check if `get_balance_due()` method exists on Invoice model
- Pass correct parameters to `openPaymentModal()`

### Appointment modal has no patients/services
- Add context variables to your view (see Step 2 above)
- Check if patients/services exist in database
- Verify template has access to context variables

### Form doesn't submit
- Check if AJAX endpoint exists (check URLs)
- Verify CSRF token is present in form
- Check browser console for AJAX errors
- Verify modal-forms library is loaded

---

## Advanced: Custom Modal Functions

You can create your own modal opener functions:

```javascript
function openCustomModal(data) {
    // Set form fields
    document.getElementById('my_field').value = data.value;
    
    // Set form action
    document.getElementById('myForm').action = `/my/ajax/endpoint/`;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('myModal'));
    modal.show();
}
```

---

## Summary

**Three simple steps:**
1. Include modals in base template
2. Add context variables to views
3. Use `onclick="openModalName(params)"` on buttons

**No page reloads, instant feedback, professional UX!**
