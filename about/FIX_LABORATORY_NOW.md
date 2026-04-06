# Fix Laboratory Migration Issue - IMMEDIATE SOLUTION

## Problem
The migration is failing because it's trying to add new fields to existing database records, and the datetime handling is causing errors.

## ✅ SOLUTION (Run these commands in order)

### Step 1: Fix the Database Schema Directly
```bash
python fix_lab_db.py
```

This script will:
- Add missing columns with proper defaults
- Rename old columns to match new model
- Update old status values

### Step 2: Delete the Problematic Migration
Delete this file:
```
laboratory/migrations/0003_alter_labtest_options_alter_labtestrequest_options_and_more.py
```

Or run:
```bash
del laboratory\migrations\0003_alter_labtest_options_alter_labtestrequest_options_and_more.py
```

### Step 3: Create a Fresh Migration
```bash
python manage.py makemigrations laboratory
```

### Step 4: Fake the New Migration
```bash
python manage.py migrate laboratory --fake
```

### Step 5: Test the Laboratory App
```bash
python manage.py runserver 192.168.100.5:8000
```

Then visit: `http://192.168.100.5:8000/laboratory/`

## Alternative: Nuclear Option (If Above Doesn't Work)

If you have NO important laboratory data yet:

```bash
# 1. Reset laboratory migrations
del laboratory\migrations\0002_*.py
del laboratory\migrations\0003_*.py

# 2. Fake unmigrate
python manage.py migrate laboratory 0001 --fake

# 3. Delete and recreate the tables
python manage.py dbshell
```

In the SQLite prompt:
```sql
DROP TABLE IF EXISTS laboratory_labtestresult;
DROP TABLE IF EXISTS laboratory_labtestrequest;
DROP TABLE IF EXISTS laboratory_labtest;
.quit
```

Then:
```bash
# 4. Create fresh migrations
python manage.py makemigrations laboratory

# 5. Apply migrations
python manage.py migrate laboratory
```

## Quick Test After Fix

Run this to verify it's working:
```python
python manage.py shell
```

Then in the shell:
```python
from laboratory.models import LabTest, LabTestRequest, LabTestResult

# Create a test
test = LabTest.objects.create(
    name='Test CBC',
    code='TEST001',
    category='hematology',
    price=25000,
    currency='UGX'
)
print(f"✓ Created test: {test}")

# Check it worked
print(f"Total tests: {LabTest.objects.count()}")
```

If that works without errors, you're good to go!

## What Caused This?

The issue occurred because:
1. Your database already had laboratory data
2. The new models added fields with `auto_now_add=True`
3. Django tried to set default values but the datetime conversion failed
4. SQLite doesn't support easily modifying existing tables

The fix scripts add the columns with proper defaults directly to the database, then we tell Django the migrations are already applied.

---

**Choose your path:**
- ✅ **Have some lab data?** → Use Step 1-5 (Recommended)
- ✅ **Starting fresh?** → Use Nuclear Option

Both will get you working!
