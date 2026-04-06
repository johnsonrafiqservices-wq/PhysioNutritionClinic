# 🔧 Troubleshooting Searchable Dropdowns

## Issue: Can't See Data or Search Not Working

### Quick Diagnosis Steps:

## Step 1: Check Browser Console 🔍

1. **Open the page:** http://172.16.61.154:8000/laboratory/
2. **Press F12** to open Developer Tools
3. **Click "Console" tab**
4. **Click "Request Test" button**
5. **Check console messages**

### What to Look For:

#### ✅ Good Signs:
```
Modal opened: requestTestModal
Dropdown: patient Options: 6
Dropdown: test Options: 9
Select2 initialized successfully
```

#### ❌ Bad Signs:
```
Dropdown: patient Options: 1  (only placeholder = no data!)
Dropdown: test Options: 1     (only placeholder = no data!)
jQuery is not defined
Select2 is not defined
```

## Step 2: Check If You Have Data 📊

Run the data checker script:

```bash
python check_lab_data.py
```

### Expected Output:

#### ✅ If You Have Data:
```
============================================================
CHECKING LABORATORY DATA
============================================================

✓ Active Patients: 5
  Sample patients:
    - John Doe (PT-000001)
    - Jane Smith (PT-000002)
    
✓ Active Lab Tests: 8
  Sample tests:
    - Complete Blood Count (hematology) - 15000 UGX
    - Blood Glucose (biochemistry) - 5000 UGX

✅ All required data exists!
```

#### ❌ If You DON'T Have Data:
```
✓ Active Patients: 0
  ⚠ WARNING: No active patients found!

✓ Active Lab Tests: 0
  ⚠ WARNING: No active lab tests found!

⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠
MISSING DATA DETECTED!
⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠⚠

Create sample data? (yes/no): 
```

**Type "yes"** to create sample data automatically!

## Step 3: Common Issues & Fixes

### Issue A: "Dropdown: patient Options: 1" (No Data)

**Cause:** No patients or tests in database

**Fix:**
```bash
# Option 1: Use the automatic script
python check_lab_data.py
# Then type "yes" when asked

# Option 2: Create via Django shell
python manage.py shell
>>> from patients.models import Patient
>>> Patient.objects.create(
...     patient_id='PT-000001',
...     first_name='John',
...     last_name='Doe',
...     date_of_birth='1990-01-01',
...     gender='M',
...     phone='0700000000',
...     is_active=True
... )
```

### Issue B: "jQuery is not defined"

**Cause:** jQuery not loading properly

**Fix:**
1. Check internet connection
2. Clear browser cache (Ctrl+F5)
3. Check if server is blocking CDN

### Issue C: Dropdown appears but no search box

**Cause:** Select2 not initializing

**Fix:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check console for JavaScript errors

### Issue D: Can see data but search doesn't work

**Cause:** Select2 initialization timing issue

**Fix:**
1. Close and reopen the modal
2. Refresh the page
3. Check browser console for errors

### Issue E: Select2 dropdown appears outside modal

**Cause:** z-index or positioning issue

**Fix:** Already fixed in base.html with:
```css
.select2-container--bootstrap-5 .select2-dropdown {
    z-index: 9999 !important;
}
```

## Step 4: Manual Testing Checklist

### Test 1: Basic Modal Opening
- [ ] Click "Request Test" button
- [ ] Modal opens
- [ ] Can see the form

### Test 2: Dropdown Visibility  
- [ ] Can see Patient dropdown
- [ ] Can see Test dropdown
- [ ] Can click to open dropdown

### Test 3: Data Presence
- [ ] Patient dropdown has more than "Select Patient"
- [ ] Test dropdown has more than "Select Test"
- [ ] Can see patient names and IDs

### Test 4: Search Functionality
- [ ] Search box appears when dropdown opens
- [ ] Can type in search box
- [ ] Results filter as you type
- [ ] Can select an option

### Test 5: Selection
- [ ] Can click to select patient
- [ ] Selected patient appears in field
- [ ] Can clear selection with X button
- [ ] Can search again

## Step 5: Browser-Specific Issues

### Chrome/Edge:
Usually works fine. If not:
1. Clear cache: Ctrl+Shift+Delete
2. Check console: F12
3. Disable extensions temporarily

### Firefox:
Usually works fine. If not:
1. Clear cache: Ctrl+Shift+Delete
2. Check console: F12
3. Try in private window

### Safari:
May have issues with Select2:
1. Update to latest Safari
2. Try Chrome instead
3. Check console for errors

## Step 6: Create Sample Data Manually

If automatic script doesn't work, use Django admin:

### Method 1: Django Admin
```
1. Go to: http://172.16.61.154:8000/admin/
2. Login with superuser
3. Click "Patients" → "Add Patient"
4. Fill form and save
5. Click "Laboratory" → "Lab Tests" → "Add Lab Test"
6. Fill form and save
```

### Method 2: Django Shell
```bash
python manage.py shell

# Create Patient
from patients.models import Patient
Patient.objects.create(
    patient_id='PT-000001',
    first_name='John',
    last_name='Doe',
    date_of_birth='1990-01-01',
    gender='M',
    phone='0700000000',
    is_active=True
)

# Create Lab Test
from laboratory.models import LabTest
LabTest.objects.create(
    name='Complete Blood Count',
    code='CBC',
    category='hematology',
    price=15000,
    currency='UGX',
    is_active=True
)
```

## Step 7: Verify Everything Works

After creating data:

1. **Refresh browser** (F5)
2. **Open laboratory page**
3. **Click "Request Test"**
4. **Check Patient dropdown:**
   - Should see "John Doe (PT-000001)"
   - Should have search box
   - Try typing "john"
   - Should filter results
5. **Check Test dropdown:**
   - Should see "Complete Blood Count - 15000 UGX"
   - Should have search box
   - Try typing "blood"
   - Should filter results

## Quick Reference

### Check Data Command:
```bash
python check_lab_data.py
```

### Browser Console Command (paste in console):
```javascript
// Check if Select2 is loaded
console.log('jQuery:', typeof $ !== 'undefined');
console.log('Select2:', typeof $.fn.select2 !== 'undefined');

// Check dropdown options
$('.modal select').each(function() {
    console.log($(this).attr('name'), 'has', this.options.length, 'options');
});
```

### Django Shell Quick Check:
```python
python manage.py shell

from patients.models import Patient
from laboratory.models import LabTest

print(f"Patients: {Patient.objects.filter(is_active=True).count()}")
print(f"Tests: {LabTest.objects.filter(is_active=True).count()}")
```

## Still Not Working?

### Final Checklist:
- [ ] Server is running
- [ ] Database migrations applied
- [ ] Sample data created
- [ ] Browser cache cleared
- [ ] No JavaScript errors in console
- [ ] jQuery is loaded
- [ ] Select2 is loaded
- [ ] Modal opens correctly

### Get More Help:
1. Check Django logs for errors
2. Check browser console (F12)
3. Run: `python check_lab_data.py`
4. Verify: http://172.16.61.154:8000/laboratory/ loads
5. Test in different browser

## Success Indicators

When everything works, you should see:

### In Browser Console:
```
Modal opened: requestTestModal
Dropdown: patient Options: 6
Dropdown: test Options: 9
```

### In Dropdown:
```
┌───────────────────────────────────┐
│ 🔍 Type to search...              │
├───────────────────────────────────┤
│ John Doe (PT-000001)              │
│ Jane Smith (PT-000002)            │
│ Michael Brown (PT-000003)         │
└───────────────────────────────────┘
```

### When Typing:
```
Type "jane" →
┌───────────────────────────────────┐
│ 🔍 jane                            │
├───────────────────────────────────┤
│ Jane Smith (PT-000002)            │ ← Filtered!
└───────────────────────────────────┘
```

---

**Most Common Solution:** Run `python check_lab_data.py` and create sample data!
