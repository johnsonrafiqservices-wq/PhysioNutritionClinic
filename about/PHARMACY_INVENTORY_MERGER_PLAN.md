# Pharmacy & Inventory Apps Merger Plan

**Date:** November 3, 2025  
**Objective:** Consolidate inventory and pharmacy apps to simplify sales management

---

## 📊 Current State Analysis

### **Inventory App (Legacy)**
```python
Models:
├── Drug (OLD medication model)
├── DrugUsage (OLD sales tracking)
├── CashFlow (financial tracking)
├── Supplier (DUPLICATE with pharmacy)
├── Prescription (DUPLICATE with pharmacy)
├── PrescriptionItem
└── Dispensing

Views:
├── drug_list, drug_edit (legacy drug management)
├── supplier_edit (duplicate functionality)
├── record_usage (old usage tracking)
├── cashflow_list
└── sales_dashboard, sales_list, sales_report, record_sale_ajax (CURRENT SALES)

URLs:
├── /inventory/ (drug management)
└── /inventory/sales/ (CURRENT SALES - using pharmacy data)

Templates:
├── drug_list.html, drug_form.html
└── sales_dashboard.html, sales_list.html, sales_report.html
```

### **Pharmacy App (Active)**
```python
Models:
├── Medication (CURRENT medication model)
├── Batch (batch management with expiry)
├── StockMovement (CURRENT sales tracking)
├── Supplier (DUPLICATE with inventory)
├── Category
├── StockAlert
├── Prescription (DUPLICATE with inventory)
├── PurchaseOrder
└── PurchaseOrderItem

Views:
├── medication_list, medication_detail (current medication management)
├── batch_list, batch_detail
├── stock_movement_list
├── supplier_list, supplier_detail
└── inventory_dashboard (pharmacy overview)

URLs:
├── /pharmacy/ (main pharmacy management)
└── /pharmacy/inventory/ (dashboard)

Templates:
├── Full pharmacy management UI
└── Modern medication/batch/stock interfaces
```

---

## 🎯 Merger Strategy

### **Phase 1: Move Sales Module to Pharmacy**

**Rationale:** Sales already use pharmacy data (StockMovement), so they belong in pharmacy app.

#### **Actions:**
1. ✅ Move sales views from `inventory/views.py` to `pharmacy/views.py`
2. ✅ Move sales URLs from `inventory/urls.py` to `pharmacy/urls.py`
3. ✅ Move sales templates from `inventory/templates/` to `pharmacy/templates/`
4. ✅ Update all URL references in templates
5. ✅ Update navigation/sidebar links

**New Structure:**
```
/pharmacy/sales/ → Sales Dashboard
/pharmacy/sales/list/ → Sales List
/pharmacy/sales/report/ → Sales Report
/pharmacy/sales/record-ajax/ → Record Sale
```

---

### **Phase 2: Keep Inventory for Legacy Data**

**Rationale:** Historical data and old Drug/DrugUsage records need to remain accessible.

#### **Keep in Inventory:**
- ✅ Drug model (read-only for historical data)
- ✅ DrugUsage model (read-only for historical sales)
- ✅ CashFlow model (financial history)
- ✅ Prescription, PrescriptionItem, Dispensing (if needed)

#### **Mark as Legacy:**
- Add `is_legacy = True` flag to models
- Admin interface for viewing only
- No new entries allowed

---

### **Phase 3: Consolidate Suppliers**

**Decision:** Use pharmacy.Supplier as primary, migrate inventory.Supplier data.

#### **Actions:**
1. ✅ Data migration script to move inventory suppliers to pharmacy
2. ✅ Update Drug model foreign key to point to pharmacy.Supplier
3. ✅ Remove inventory.Supplier model (after migration)

---

### **Phase 4: Update Navigation & UI**

#### **Sidebar Navigation:**
```
📦 Pharmacy (Main Section)
├── 📊 Dashboard
├── 💊 Medications
├── 📦 Batches
├── 📋 Stock Movements
├── 🏢 Suppliers
├── 💰 Sales (NEW LOCATION)
│   ├── Sales Dashboard
│   ├── View All Sales
│   └── Sales Report
└── 📝 Prescriptions

📚 Inventory (Legacy - Optional)
└── 📜 Historical Data
    ├── Old Drugs (read-only)
    └── Old Sales (read-only)
```

---

## 📁 Detailed File Changes

### **1. Move Sales Views**

**From:** `inventory/views.py`
**To:** `pharmacy/views.py`

```python
# Move these functions:
- sales_dashboard()
- sales_list()
- sales_report()
- record_sale_ajax()

# Already using pharmacy models, so minimal changes needed
```

---

### **2. Move Sales URLs**

**From:** `inventory/urls.py`
```python
# Remove:
path('sales/', views.sales_dashboard, name='sales_dashboard'),
path('sales/list/', views.sales_list, name='sales_list'),
path('sales/report/', views.sales_report, name='sales_report'),
path('sales/record-ajax/', views.record_sale_ajax, name='record_sale_ajax'),
```

**To:** `pharmacy/urls.py`
```python
# Add:
path('sales/', views.sales_dashboard, name='sales_dashboard'),
path('sales/list/', views.sales_list, name='sales_list'),
path('sales/report/', views.sales_report, name='sales_report'),
path('sales/record-ajax/', views.record_sale_ajax, name='record_sale_ajax'),
```

---

### **3. Move Sales Templates**

**From:** `templates/inventory/`
**To:** `templates/pharmacy/`

```
sales_dashboard.html
sales_list.html
sales_report.html
```

**Update all URL references:**
```django
<!-- OLD -->
{% url 'inventory:sales_dashboard' %}
{% url 'inventory:sales_list' %}
{% url 'inventory:sales_report' %}
{% url 'inventory:record_sale_ajax' %}

<!-- NEW -->
{% url 'pharmacy:sales_dashboard' %}
{% url 'pharmacy:sales_list' %}
{% url 'pharmacy:sales_report' %}
{% url 'pharmacy:record_sale_ajax' %}
```

---

### **4. Update Navigation**

**File:** `templates/base.html`

```django
<!-- OLD -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'inventory:sales_dashboard' %}">
        <i class="bi bi-cart-check"></i> Sales
    </a>
</li>

<!-- NEW -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'pharmacy:sales_dashboard' %}">
        <i class="bi bi-cart-check"></i> Sales
    </a>
</li>
```

---

## 🔄 Migration Strategy

### **Step 1: Supplier Data Migration**

```python
# Create migration script
from django.core.management.base import BaseCommand
from inventory.models import Supplier as OldSupplier
from pharmacy.models import Supplier as NewSupplier

class Command(BaseCommand):
    def handle(self, *args, **options):
        for old_supplier in OldSupplier.objects.all():
            # Check if already migrated
            if not NewSupplier.objects.filter(name=old_supplier.name).exists():
                NewSupplier.objects.create(
                    name=old_supplier.name,
                    country=old_supplier.country,
                    contact=old_supplier.contact,
                    email=old_supplier.email,
                    address=old_supplier.address,
                    is_active=old_supplier.is_active
                )
```

---

### **Step 2: Update Foreign Keys**

```python
# Update Drug model to use pharmacy.Supplier
from pharmacy.models import Supplier as PharmacySupplier

class Drug(models.Model):
    # ... other fields ...
    supplier = models.ForeignKey(
        PharmacySupplier, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
```

---

## 📊 Benefits of Merger

### **1. Simplified Architecture**
- ✅ One app for all medication/sales management
- ✅ No confusion about which model to use
- ✅ Clear data flow

### **2. Better Code Organization**
```
pharmacy/ (MAIN APP)
├── Medication management
├── Batch management
├── Stock movements
├── Sales tracking
├── Supplier management
└── Prescriptions

inventory/ (LEGACY)
└── Historical data only
```

### **3. Improved User Experience**
- ✅ All pharmacy features in one place
- ✅ Consistent navigation
- ✅ No jumping between apps

### **4. Development Benefits**
- ✅ Single source of truth
- ✅ Easier maintenance
- ✅ Better testing
- ✅ Clearer documentation

---

## 🎯 Implementation Checklist

### **Phase 1: Move Sales (2-3 hours)**
- [ ] Copy sales views to pharmacy/views.py
- [ ] Add sales URLs to pharmacy/urls.py
- [ ] Move sales templates to pharmacy/templates/
- [ ] Update all URL references in templates
- [ ] Update navigation in base.html
- [ ] Test all sales functionality
- [ ] Remove sales code from inventory app

### **Phase 2: Supplier Migration (1 hour)**
- [ ] Create migration command
- [ ] Run supplier data migration
- [ ] Update Drug model foreign key
- [ ] Run makemigrations and migrate
- [ ] Test supplier functionality
- [ ] Remove inventory.Supplier model

### **Phase 3: Documentation (1 hour)**
- [ ] Update README
- [ ] Update API documentation
- [ ] Create migration notes
- [ ] Update user guide

### **Phase 4: Legacy Cleanup (1 hour)**
- [ ] Mark inventory models as legacy
- [ ] Update admin interfaces
- [ ] Add read-only restrictions
- [ ] Archive old templates

---

## ⚠️ Risks & Mitigation

### **Risk 1: Broken URL References**
**Mitigation:** 
- Comprehensive template search for `inventory:sales`
- Update all references before removal
- Keep redirects temporarily

### **Risk 2: Data Loss**
**Mitigation:**
- Backup database before migration
- Test migration on staging first
- Keep inventory app data intact

### **Risk 3: User Confusion**
**Mitigation:**
- Update user documentation
- Add announcement of URL changes
- Provide training if needed

---

## 🚀 Post-Merger Structure

### **Final App Organization**

```
pharmacy/ (PRIMARY APP)
├── models.py
│   ├── Medication (current inventory)
│   ├── Batch (with expiry tracking)
│   ├── StockMovement (all movements including sales)
│   ├── Supplier (consolidated)
│   ├── Category
│   ├── StockAlert
│   ├── Prescription
│   ├── PurchaseOrder
│   └── PurchaseOrderItem
├── views.py
│   ├── Medication management
│   ├── Batch management
│   ├── Stock movements
│   ├── Supplier management
│   ├── Sales dashboard (MOVED)
│   ├── Sales list (MOVED)
│   ├── Sales report (MOVED)
│   └── Record sale AJAX (MOVED)
└── urls.py
    ├── /pharmacy/ (main)
    ├── /pharmacy/medications/
    ├── /pharmacy/batches/
    ├── /pharmacy/stock/
    ├── /pharmacy/suppliers/
    └── /pharmacy/sales/ (MOVED)

inventory/ (LEGACY APP - Optional)
├── models.py (read-only)
│   ├── Drug (historical)
│   ├── DrugUsage (historical)
│   └── CashFlow (historical)
└── admin.py (view only)
```

---

## 📈 Success Metrics

### **Completion Criteria:**
- ✅ All sales URLs work under /pharmacy/sales/
- ✅ No broken links in templates
- ✅ Sales dashboard displays correctly
- ✅ Record sale modal works
- ✅ Sales reports generate correctly
- ✅ Navigation updated
- ✅ Documentation updated

### **Performance Metrics:**
- ✅ No increase in page load time
- ✅ All tests pass
- ✅ No database errors
- ✅ User workflows unchanged

---

## 🎉 Conclusion

This merger will:
1. **Simplify** the codebase by consolidating related functionality
2. **Improve** user experience with clear app organization
3. **Maintain** historical data integrity
4. **Enable** future enhancements in a single, focused app

**Estimated Total Time:** 5-6 hours  
**Recommended Approach:** Phase-by-phase implementation with testing between phases  
**Priority:** High (improves maintainability and user experience)

---

## 📝 Next Steps

1. **Review this plan** with the team
2. **Backup database** before starting
3. **Create a feature branch** for the merger
4. **Implement Phase 1** (Move Sales)
5. **Test thoroughly**
6. **Deploy to staging**
7. **Get user feedback**
8. **Deploy to production**

---

**Status:** 📋 PLAN READY - AWAITING APPROVAL
