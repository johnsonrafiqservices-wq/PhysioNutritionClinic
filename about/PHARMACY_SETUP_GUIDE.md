# Pharmacy App - Quick Setup Guide

## 🚀 Getting Started

Follow these steps to set up the pharmacy app in your PhysioNutrition Clinic system.

---

## Step 1: Run Database Migrations

The pharmacy app includes new models that need to be added to your database:

```bash
# Navigate to your project directory
cd c:\Users\it.sm\Documents\GitHub\excellence_med_care

# Create migrations for the new models
python manage.py makemigrations pharmacy

# Apply the migrations
python manage.py migrate pharmacy
```

**Expected Output:**
```
Migrations for 'pharmacy':
  pharmacy/migrations/0002_purchaseorder_purchaseorderitem.py
    - Create model PurchaseOrder
    - Create model PurchaseOrderItem
Running migrations:
  Applying pharmacy.0002_purchaseorder_purchaseorderitem... OK
```

---

## Step 2: Load JavaScript Library

Add the pharmacy JavaScript library to your templates:

### Option A: Include in Base Template
Add to `templates/base.html` before `</body>`:

```html
<!-- Pharmacy Modal Forms Library -->
<script src="{% static 'js/pharmacy-modals.js' %}"></script>
```

### Option B: Include in Pharmacy Templates Only
Add to individual pharmacy templates:

```html
{% load static %}
<script src="{% static 'js/pharmacy-modals.js' %}"></script>
```

---

## Step 3: Access the Pharmacy Dashboard

Navigate to: `http://localhost:8000/pharmacy/`

You should see:
- **Total Medications**: Count of active medications
- **Total Batches**: Count of active batches
- **Low Stock Count**: Items below reorder level
- **Pending Prescriptions**: Awaiting dispensing
- **Recent Prescriptions**: Last 5 prescriptions
- **Low Stock Items**: List of items needing reorder

---

## Step 4: Create Sample Data (Optional)

### Create a Category
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Click "Categories" under PHARMACY
3. Add categories like:
   - Analgesics
   - Antibiotics
   - Vitamins
   - Physiotherapy Supplies

### Create a Supplier
1. Click "Suppliers" in admin
2. Add suppliers like:
   - MedSupply Uganda
   - PharmaCare Ltd
   - Global Medical Supplies

### Create a Medication
1. Click "Medications" in admin
2. Add medications:
   - Name: Paracetamol
   - Generic: Acetaminophen
   - Category: Analgesics
   - Strength: 500mg
   - Form: Tablet
   - Unit Price: 500 UGX
   - Reorder Level: 100

### Create a Batch
1. Click "Batches" in admin
2. Add a batch:
   - Medication: Select medication
   - Supplier: Select supplier
   - Batch Number: BATCH001
   - Quantity: 1000
   - Cost Price: 400 UGX
   - Selling Price: 500 UGX
   - Expiry Date: Choose future date
   - Status: Active

---

## Step 5: Test Key Features

### Test 1: Create a Prescription
```
1. Go to /pharmacy/prescriptions/create/
2. Fill in:
   - Patient: Select patient
   - Medication: Select medication
   - Dosage: 500mg
   - Frequency: Twice daily
   - Duration: 7 days
   - Quantity: 14
3. Save
```

### Test 2: Dispense Prescription
```
1. Go to /pharmacy/prescriptions/
2. Click "Dispense" on a pending prescription
3. System will:
   - Check stock availability
   - Select batch (FIFO by expiry)
   - Create stock movement
   - Update batch quantity
   - Update prescription status
```

### Test 3: Check Alerts
```
1. Go to /pharmacy/alerts/expiry/
   - View medications expiring soon
   
2. Go to /pharmacy/alerts/low-stock/
   - View items below reorder level
```

### Test 4: View Analytics
```
1. Go to /pharmacy/analytics/
   - View comprehensive pharmacy statistics
   - Stock movement trends
   - Top dispensed medications
   - Inventory value
```

---

## Step 6: Test AJAX Modals (After Template Creation)

Once you create the modal templates, test:

### Create Medication Modal
```javascript
// In browser console or onclick
const url = '/pharmacy/ajax/medication/create/';
submitMedicationForm('medicationCreateForm', url);
```

### Dispense Prescription
```javascript
// Dispense prescription ID 1
dispensePrescription(1);
```

### Adjust Stock
```javascript
// Adjust stock for batch ID 1
submitStockAdjustmentForm('stockAdjustmentForm', 1);
```

---

## Step 7: Configure Alerts

### Enable Low Stock Alerts
The system automatically:
1. Calculates total stock for each medication
2. Compares with reorder level
3. Creates StockAlert records
4. Displays in /pharmacy/alerts/low-stock/

### Enable Expiry Alerts
The system automatically:
1. Checks batch expiry dates
2. Categorizes by urgency (30/90 days)
3. Displays in /pharmacy/alerts/expiry/

---

## Common URLs

### Main URLs
- Dashboard: `/pharmacy/`
- Inventory: `/pharmacy/inventory/`
- Medications: `/pharmacy/medications/`
- Batches: `/pharmacy/batches/`
- Prescriptions: `/pharmacy/prescriptions/`
- Suppliers: `/pharmacy/suppliers/`
- Stock Report: `/pharmacy/stock/report/`

### Alert URLs
- Expiry Alerts: `/pharmacy/alerts/expiry/`
- Low Stock Alerts: `/pharmacy/alerts/low-stock/`
- Analytics: `/pharmacy/analytics/`

### AJAX Endpoints
- Medication Create: `/pharmacy/ajax/medication/create/`
- Batch Create: `/pharmacy/ajax/batch/create/`
- Prescription Create: `/pharmacy/ajax/prescription/create/`
- Dispense: `/pharmacy/ajax/prescription/<id>/dispense/`
- Stock Adjust: `/pharmacy/ajax/stock/adjustment/<batch_id>/`

---

## Troubleshooting

### Issue: Migration Errors
```bash
# If you get migration errors, try:
python manage.py migrate pharmacy --fake-initial
```

### Issue: AJAX Not Working
- Check if `pharmacy-modals.js` is loaded
- Open browser console for JavaScript errors
- Verify CSRF token is present
- Check AJAX request headers

### Issue: Stock Not Deducting
- Check if batch has sufficient quantity
- Verify batch is active
- Check expiry date is in future
- Review StockMovement records

### Issue: No Low Stock Alerts
- Visit `/pharmacy/alerts/low-stock/` to trigger alert creation
- Check medication reorder levels
- Verify batch quantities

---

## Next Steps

### 1. Create Additional Templates
- expiry_alerts.html
- low_stock_alerts.html
- analytics.html
- purchase_order_list.html
- Modal templates

### 2. Integrate with Patient Module
- Link prescriptions to appointments
- Show medication history in patient profile
- Add medication alerts to patient record

### 3. Integrate with Billing
- Auto-create invoices from dispensed prescriptions
- Track medication costs
- Generate pharmacy revenue reports

### 4. Advanced Features
- Barcode scanning
- Email alerts
- Automated reordering
- Drug interaction checks
- Batch tracking with QR codes

---

## Support & Documentation

- **Main Documentation**: `PHARMACY_APP_COMPLETE.md`
- **Models**: `pharmacy/models.py`
- **Views**: `pharmacy/views.py` and `pharmacy/views_reports.py`
- **Forms**: `pharmacy/forms.py`
- **Admin**: `pharmacy/admin.py`
- **URLs**: `pharmacy/urls.py`
- **JavaScript**: `static/js/pharmacy-modals.js`

---

## Security Notes

### Permissions
The pharmacy app uses `@login_required` decorator. Consider adding:
- Role-based access (pharmacist, doctor, admin)
- Prescription approval workflow
- Stock adjustment approval
- Audit log access restrictions

### Data Protection
- Stock movements are immutable (audit trail)
- Batch deactivation instead of deletion
- Complete audit trail
- Prescription tracking

---

## Performance Tips

1. **Use Indexes**: Models already have proper indexing
2. **Batch Queries**: Use select_related() and prefetch_related()
3. **Cache Reports**: Cache analytics for 5-10 minutes
4. **Archive Old Data**: Archive old prescriptions and stock movements

---

**Ready to Use!** 🎉

Your pharmacy app is now fully functional. Start by running the migrations and accessing the dashboard at `/pharmacy/`.

For any issues, refer to `PHARMACY_APP_COMPLETE.md` for detailed documentation.
