# Batch Modal Not Working - Debugging Guide

## Quick Fix - Run This First!

Open your terminal in the project directory and run:

```bash
python manage.py collectstatic --noinput
```

**Why?** Django needs to collect static files (including `pharmacy-modals.js`) to serve them. Without this, the JavaScript file won't load even though it exists in the code.

---

## Step-by-Step Troubleshooting

### Step 1: Check Browser Console
1. Open the batch list page
2. Press **F12** (or right-click → Inspect)
3. Go to **Console** tab
4. Look for errors like:
   - `Failed to load resource: pharmacy-modals.js`
   - `submitBatchForm is not defined`
   - `404 Not Found: /static/js/pharmacy-modals.js`

### Step 2: If You See 404 Error
**Run collectstatic:**
```bash
python manage.py collectstatic --noinput
```

Then refresh the page and try again.

### Step 3: Check Network Tab
1. In browser DevTools, go to **Network** tab
2. Refresh the page
3. Look for `pharmacy-modals.js` in the list
4. **If it's red (404)**: Run collectstatic
5. **If it's green (200)**: The file loaded correctly

### Step 4: Test the Function
In the browser console, type:
```javascript
typeof submitBatchForm
```

**Expected result:** `"function"`
**If you get:** `"undefined"` → File didn't load, run collectstatic

---

## Common Issues & Solutions

### Issue 1: Static Files Not Collected
**Symptom:** Console error: "submitBatchForm is not defined"

**Solution:**
```bash
python manage.py collectstatic --noinput
```

### Issue 2: Development Server Cache
**Symptom:** Changes not showing up

**Solution:**
1. Stop the server (Ctrl+C)
2. Run: `python manage.py collectstatic --noinput`
3. Clear browser cache (Ctrl+Shift+Delete)
4. Restart server: `python manage.py runserver`
5. Hard refresh page (Ctrl+F5)

### Issue 3: Missing Required Fields
**Symptom:** Form submits but gets validation errors

**Check these required fields:**
- Medication (select one)
- Supplier (select one)
- Batch Number (text)
- Quantity (number)
- Cost Price (number)
- Selling Price (number)
- Expiry Date (date)

### Issue 4: Form Not Submitting at All
**Check:**
1. Is the modal opening? (If not, check Bootstrap is loaded)
2. Is the button clickable? (Check for overlays)
3. Any JavaScript errors in console?

---

## Manual Testing Checklist

### ✅ Before Testing:
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Restart Django server
- [ ] Clear browser cache
- [ ] Hard refresh page (Ctrl+F5)

### ✅ Test Batch Creation:
1. [ ] Open Pharmacy → Batches
2. [ ] Click "Receive Batch" button
3. [ ] Modal opens properly
4. [ ] Medication dropdown shows options
5. [ ] Supplier dropdown shows options
6. [ ] Fill all required fields:
   - [ ] Select medication
   - [ ] Select supplier
   - [ ] Batch number: TEST-001
   - [ ] Quantity: 100
   - [ ] Cost price: 5000
   - [ ] Selling price: 7000
   - [ ] Expiry date: (future date)
7. [ ] Click "Save Batch"
8. [ ] Success message appears
9. [ ] Modal closes
10. [ ] Page redirects to batch list
11. [ ] New batch appears in list

---

## Advanced Debugging

### Check Static Files Configuration

In `clinic_system/settings.py`, verify:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Check File Actually Exists

**Windows:**
```bash
dir static\js\pharmacy-modals.js
```

**Expected:** File should be listed

### Check File Permissions

Make sure the file is readable:
```bash
icacls static\js\pharmacy-modals.js
```

Should show read permissions.

### Check Template Loading

Add this temporarily to `batch_list.html` to verify:
```html
<script>
console.log('Template loaded');
console.log('submitBatchForm:', typeof submitBatchForm);
</script>
```

**Expected in console:**
```
Template loaded
submitBatchForm: function
```

---

## If Still Not Working

### Last Resort Fix:

1. **Stop the server**

2. **Clear everything:**
```bash
python manage.py collectstatic --clear --noinput
```

3. **Collect fresh:**
```bash
python manage.py collectstatic --noinput
```

4. **Clear browser completely:**
   - Chrome: Ctrl+Shift+Delete → Check "Cached images and files" → Clear
   - Firefox: Ctrl+Shift+Delete → Check "Cache" → Clear

5. **Restart Django:**
```bash
python manage.py runserver
```

6. **Open in private/incognito window:**
   - Ctrl+Shift+N (Chrome)
   - Ctrl+Shift+P (Firefox)

7. **Test again**

---

## Quick Reference - Console Commands

```bash
# Collect static files (RUN THIS FIRST!)
python manage.py collectstatic --noinput

# Clear and recollect
python manage.py collectstatic --clear --noinput

# Check if JavaScript functions are loaded (in browser console)
typeof submitBatchForm

# Should return: "function"
```

---

## Success Indicators

### ✅ Everything Working:
1. No console errors
2. `typeof submitBatchForm` returns `"function"`
3. Clicking "Save Batch" shows loading state
4. Validation errors display if fields empty
5. Success message appears when form valid
6. Modal closes and redirects

### ❌ Still Broken:
1. Console shows "not defined" error
2. Button click does nothing
3. No network request in Network tab
4. File shows 404 in Network tab

**If still broken after collectstatic:** Check that Django development server is running and accessible at the correct port.

---

## Contact Information

If you've tried everything above and it's still not working, check:
1. Django version compatibility
2. Browser compatibility (use Chrome/Firefox)
3. Any JavaScript errors in console
4. Server logs for Python errors

**Most Common Solution:** Just run `python manage.py collectstatic --noinput` and refresh!
