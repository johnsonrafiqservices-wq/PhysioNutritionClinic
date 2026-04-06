# Prescription Total Amount - Debug Steps

## ✅ Changes Applied

I've made the following fixes to resolve the total amount display issue:

### Fix 1: Removed setTimeout Conflict
**Line 1565-1567** - Removed the `setTimeout` that was calling `updateCalculations()` after 1 second, which was resetting the total to UGX 0.

### Fix 2: Added Prescription Mode Check
**Line 1602-1608** - Modified `updateCalculations()` to skip when in prescription mode (total is set by AJAX, not by dropdown calculation).

### Fix 3: Enhanced Logging
Added comprehensive console logging to track the entire flow:
- When prescription is selected
- AJAX request URL
- Server response
- Total amount update

## 🔍 Troubleshooting Steps

### Step 1: Clear Browser Cache
**CRITICAL:** You must clear your browser cache or hard refresh!

**Windows:**
- Chrome/Edge: Press `Ctrl + Shift + R` or `Ctrl + F5`
- Firefox: Press `Ctrl + Shift + R`

**Or clear cache manually:**
1. Press `F12` to open Developer Tools
2. Right-click the refresh button
3. Click "Empty Cache and Hard Reload"

### Step 2: Open Developer Console
1. Press `F12` to open Developer Tools
2. Click on the **Console** tab
3. Leave it open while testing

### Step 3: Test Prescription Selection

1. Navigate to: `http://192.168.100.5:8000/pharmacy/sales/`
2. Click **"Record Sale"** button
3. Select **"Prescription"** radio button
4. Open the prescription dropdown
5. Select ANY prescription from the list

### Step 4: Check Console Output

You should see this in the console:

```
🔔 Prescription dropdown changed!
Selected option: <option>...
Selected value: 1
📋 Prescription selected: {prescriptionId: "1", medicationId: "...", ...}
📡 Fetching prescription total from: /pharmacy/ajax/prescription/1/total/
📥 Response received: 200 OK
📦 Response data: {success: true, total_amount: 16800, items: [...]}
💵 Total amount from server: 16800
💰 Prescription total formatted: UGX 16,800
✅ Total amount updated in UI: UGX 16,800
```

### Step 5: Check Visual Display

After selecting a prescription, you should see:

**In the "Total Amount" section:**
```
Total Amount: UGX 16,800 (or whatever the prescription total is)
```

**In the prescription info box:**
```
✓ Ready to Dispense
Patient: RATIFAH ISA
Prescription: 1 medication
Total: UGX 16,800
✅ Click "Dispense Medication" to complete
```

## 🚨 If Total Still Shows "UGX 0"

### Check 1: Verify Prescriptions Exist
Run this in Django shell:
```bash
python manage.py shell
```
```python
from pharmacy.models import Prescription
prescriptions = Prescription.objects.filter(status='pending')
print(f"Pending prescriptions: {prescriptions.count()}")
for p in prescriptions[:3]:
    print(f"  - {p.id}: {p.patient} - {p}")
```

### Check 2: Test AJAX Endpoint Directly
Open this URL in your browser (replace `1` with actual prescription ID):
```
http://192.168.100.5:8000/pharmacy/ajax/prescription/1/total/
```

**Expected Response:**
```json
{
    "success": true,
    "total_amount": 16800.0,
    "items": [
        {
            "medication": "Cetirizine",
            "quantity": 28,
            "unit_price": 600.0,
            "total": 16800.0
        }
    ],
    "medication_count": 1
}
```

**If you get an error:**
- Check that the prescription ID exists
- Ensure medications have batches with stock
- Check Django logs for errors

### Check 3: Console Errors
Look for any RED errors in the browser console:

**Common errors:**
- `404 Not Found` - Check URL routing
- `500 Server Error` - Check Django logs
- `estimatedRevenue element not found` - Check HTML structure
- CORS errors - Check headers

### Check 4: Verify Element Exists
In the browser console, run:
```javascript
document.getElementById('estimatedRevenue')
```

**Expected:** Should show the `<span>` element  
**If null:** The HTML structure has changed

### Check 5: Manual Test
In the browser console, manually set the total:
```javascript
document.getElementById('estimatedRevenue').textContent = 'UGX 25,000';
```

**If this works:** The JavaScript is running correctly  
**If this doesn't work:** There's an HTML structure issue

## 🐛 Common Issues

### Issue 1: Browser Cache
**Symptom:** Console shows old code or no new logs  
**Solution:** Hard refresh with `Ctrl + Shift + R`

### Issue 2: No Prescriptions
**Symptom:** Dropdown is empty or shows "No pending prescriptions"  
**Solution:** Run `python manage.py populate_prescriptions`

### Issue 3: Medications Have No Stock
**Symptom:** Response shows `total_amount: 0` or `error: 'No stock available'`  
**Solution:** Run `python manage.py populate_medications`

### Issue 4: AJAX Request Fails
**Symptom:** Console shows network error or 404  
**Solution:** Check that pharmacy URLs are properly configured

### Issue 5: UpdateCalculations Interference
**Symptom:** Total briefly appears then resets to UGX 0  
**Solution:** Already fixed - updateCalculations now skips prescription mode

## 📊 Expected Console Log Sequence

When everything is working correctly:

```
1. 🔔 Prescription dropdown changed!
2. Selected value: 1
3. 📋 Prescription selected: {...}
4. 📡 Fetching prescription total from: /pharmacy/ajax/prescription/1/total/
5. 🔢 updateCalculations skipped - prescription mode (total set by AJAX)
6. 📥 Response received: 200 OK
7. 📦 Response data: {success: true, ...}
8. 💵 Total amount from server: 16800
9. 💰 Prescription total formatted: UGX 16,800
10. ✅ Total amount updated in UI: UGX 16,800
11. 💰 Prescription total is set via AJAX - no calculation needed
```

## ✅ Testing Checklist

- [ ] Hard refresh browser (Ctrl + Shift + R)
- [ ] Open Developer Console (F12)
- [ ] Navigate to sales dashboard
- [ ] Click "Record Sale"
- [ ] Select "Prescription" sale type
- [ ] Select a prescription from dropdown
- [ ] Check console for log messages
- [ ] Verify "Total Amount" displays correct value
- [ ] Verify prescription info shows total
- [ ] Try different prescriptions
- [ ] Verify totals match expected amounts

## 🎯 Quick Test URLs

### Sales Dashboard
```
http://192.168.100.5:8000/pharmacy/sales/
```

### Test Prescription Total API (Prescription ID 1)
```
http://192.168.100.5:8000/pharmacy/ajax/prescription/1/total/
```

### Pharmacy Dashboard
```
http://192.168.100.5:8000/pharmacy/
```

## 📝 Send Me This Info

If it's still not working, send me:

1. **Console Output:** Copy all console messages after selecting prescription
2. **Network Tab:** Any failed requests (red in Network tab of Dev Tools)
3. **Prescription Data:** Which prescription did you select?
4. **Expected vs Actual:** What total should show vs what shows

## 🆘 Emergency Reset

If everything is broken:

```bash
# 1. Clear all sample data
python manage.py shell
>>> from pharmacy.models import Prescription, Medication, Batch
>>> Prescription.objects.filter(status='pending').delete()

# 2. Recreate sample data
python manage.py populate_medications
python manage.py populate_prescriptions

# 3. Clear browser cache completely
# Settings → Privacy → Clear browsing data → Cached images and files

# 4. Restart Django server
Ctrl+C
python manage.py runserver 192.168.100.5:8000
```

---
**Updated:** November 13, 2025, 10:57 PM  
**Status:** Fixes applied, awaiting user testing  
**Next Step:** Clear browser cache and test with console open
