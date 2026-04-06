# Sales Recording Process - Testing Checklist

## Prerequisites Check

### 1. Check if Medications Exist
```python
python manage.py shell
from pharmacy.models import Medication
print(f"Total medications: {Medication.objects.count()}")
print(f"Active medications: {Medication.objects.filter(is_active=True).count()}")
```

### 2. Check if Batches Exist
```python
from pharmacy.models import Batch
from django.utils import timezone
active_batches = Batch.objects.filter(
    is_active=True,
    quantity_remaining__gt=0,
    expiry_date__gte=timezone.now().date()
)
print(f"Available batches: {active_batches.count()}")
for batch in active_batches[:5]:
    print(f"  - {batch.medication.name}: {batch.batch_number} (Stock: {batch.quantity_remaining})")
```

## Testing Flow

### Step 1: Navigate to Sales List
- URL: `http://172.16.61.154:8000/pharmacy/sales/list/`
- Should see sales list page with "Record Sale" button

### Step 2: Open Record Sale Modal
- Click "Record Sale" button
- Modal should open
- Check browser console (F12) for:
  ```
  Loading medications...
  Response status: 200
  Medications data: {...}
  Loaded X medications
  ```

### Step 3: Verify Medications Load
- Medication dropdown should populate
- Should see medications in format: "Name (Generic Name)"
- Dropdown should be enabled

### Step 4: Select Medication
- Click medication dropdown
- Select a medication
- Check console for:
  ```
  Loading batches for medication: X
  Batch response status: 200
  Batches data: {...}
  Loaded X batches
  ```

### Step 5: Verify Batches Load
- Batch dropdown should populate
- Should see batches in format: "Batch# (Stock: X, Exp: YYYY-MM-DD)"
- Dropdown should be enabled

### Step 6: Select Batch
- Click batch dropdown
- Select a batch
- Verify:
  - Stock info displays
  - Expiry date shows
  - Unit price auto-fills
  - Max quantity is set

### Step 7: Enter Quantity
- Enter a quantity (e.g., 2)
- Verify total amount calculates automatically
- Should show: Unit Price × Quantity

### Step 8: Submit Sale
- Click "Record Sale" button
- Button should show "Recording..." with spinner
- Check server console for:
  ```
  record_sale_ajax called
  POST data: <QueryDict...>
  Batch ID: X, Quantity: Y
  Batch found: ..., Stock: ...
  Creating stock movement: SALE-...
  Stock movement created: ID X
  Batch stock updated: X -> Y
  Revenue calculated: ...
  Sale successful: Sale recorded successfully! ...
  Returning response: {...}
  ```

### Step 9: Verify Success
- Alert should show "Sale recorded successfully!"
- Page should reload
- New sale should appear in list

## Error Scenarios to Test

### 1. Insufficient Stock
- Try to sell more than available
- Should show: "Insufficient stock. Only X units available."

### 2. No Batches Available
- Select medication with no batches
- Should show: "No batches available"

### 3. Expired Batches
- Batches with expired dates should not appear

### 4. Invalid Quantity
- Try negative or zero quantity
- Should be prevented by form validation

## Debug Commands

### Check Server Logs
```bash
# Server should print:
get_medications_ajax called
Found X medications
Returning X medications

get_batches_ajax called for medication_id: X
Found X batches for medication X
Returning X batches

record_sale_ajax called
POST data: <QueryDict: {'batch': ['X'], 'quantity': ['Y'], ...}>
Batch ID: X, Quantity: Y
...
Sale successful: ...
```

### Check Database After Sale
```python
from pharmacy.models import StockMovement, Batch
latest_sale = StockMovement.objects.filter(movement_type='out', reference__icontains='SALE').latest('created_at')
print(f"Latest sale: {latest_sale.reference}")
print(f"Medication: {latest_sale.batch.medication.name}")
print(f"Quantity: {latest_sale.quantity}")
print(f"Remaining stock: {latest_sale.batch.quantity_remaining}")
```

## Common Issues & Fixes

### Issue: Medications Not Loading
**Fix:**
1. Check URL endpoint: `/pharmacy/ajax/medications/list/`
2. Verify medications exist and are active
3. Check browser console for errors
4. Check server logs

### Issue: Batches Not Loading
**Fix:**
1. Check URL endpoint: `/pharmacy/ajax/batches/list/`
2. Verify batches exist for selected medication
3. Check batches are active, have stock, and not expired
4. Check server logs

### Issue: Sale Not Recording
**Fix:**
1. Check form data in browser console
2. Check server logs for errors
3. Verify batch exists and has stock
4. Check CSRF token is present

### Issue: Stock Not Updating
**Fix:**
1. Check stock movement was created
2. Verify batch.save() was called
3. Check for database transaction errors
