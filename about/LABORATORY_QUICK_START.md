# Laboratory System - Quick Start

## 🚀 Immediate Setup (2 Minutes)

### 1. Run Migrations
```bash
python manage.py makemigrations laboratory
python manage.py migrate
```

### 2. Access the Laboratory
```
http://localhost:8000/laboratory/
```

### 3. Add Sample Tests (Optional)
Run in Django shell (`python manage.py shell`):
```python
from laboratory.models import LabTest

LabTest.objects.create(
    name='Complete Blood Count',
    code='CBC001',
    category='hematology',
    price=25000,
    currency='UGX',
    sample_type='Blood',
    duration_hours=2
)
```

## 📱 Quick Access URLs

| Feature | URL |
|---------|-----|
| Dashboard | `/laboratory/` |
| Test Catalog | `/laboratory/tests/` |
| Request Test | `/laboratory/requests/create/` |
| All Requests | `/laboratory/requests/` |
| Add Result | `/laboratory/results/add/` |
| View Results | `/laboratory/results/` |

## 👥 User Roles

Access is granted to users with these roles:
- `admin` - Full access
- `doctor` - Request & view
- `nurse` - Request & view  
- `lab_tech` - Add results & manage

**Adjust roles in** `base.html` line 449 if needed.

## 🔄 Common Workflows

### Request a Lab Test
1. Laboratory → Request Test
2. Select patient and test
3. Set priority (Routine/Urgent/STAT)
4. Add clinical notes
5. Submit

### Add Test Result
1. Laboratory → Lab Requests
2. Click on pending request
3. Click "Add Result"
4. Enter values and interpretation
5. Mark as abnormal if needed
6. Submit

### View Patient Lab History
1. Go to patient detail page
2. View lab_requests section
3. Click on any request to see results

## 🎨 Features at a Glance

✅ Test catalog with 7 categories  
✅ Request tracking (5 status levels)  
✅ Priority system (Routine/Urgent/STAT)  
✅ Result entry with verification  
✅ Search & filter capabilities  
✅ Modern responsive UI  
✅ Statistics dashboard  
✅ Django admin integration  

## 💡 Pro Tips

1. **Use Test Codes**: Create systematic codes like CBC001, GLUC001 for easy reference
2. **Set Normal Ranges**: Helps lab techs identify abnormal results quickly
3. **Add Duration**: Sets expectations for when results will be available
4. **Use Priorities**: STAT for emergency, Urgent for same-day, Routine for standard
5. **Clinical Notes**: Help lab understand context and process appropriately

## 🐛 Common Issues

**Can't see Laboratory menu?**
- Check user role in database
- Verify role matches condition in base.html line 449

**Template errors?**
- Ensure `laboratory` is in INSTALLED_APPS
- Run `python manage.py collectstatic` if needed

**Migration conflicts?**
- Try: `python manage.py migrate laboratory --fake`
- Or: Delete `laboratory/migrations/` except `__init__.py`, then remake migrations

## 📞 Quick Commands

```bash
# Check if migrations needed
python manage.py makemigrations --dry-run

# Apply migrations
python manage.py migrate laboratory

# Create superuser (if needed)
python manage.py createsuperuser

# Load sample data (if you created fixtures)
python manage.py loaddata laboratory_tests.json

# Shell access
python manage.py shell
```

## 🎯 What's Next?

After basic setup:
1. Add your clinic's standard tests via admin or forms
2. Train staff on requesting tests
3. Set up lab tech accounts for result entry
4. Consider PDF report generation
5. Integrate with billing system

---

**Ready to use!** Visit `/laboratory/` to get started.

For detailed information, see `LABORATORY_SETUP_GUIDE.md`
