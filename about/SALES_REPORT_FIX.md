# Sales Report FieldError - FIXED

**Date:** November 3, 2025  
**Status:** ✅ RESOLVED

---

## 🐛 Error Encountered

```
FieldError at /inventory/sales/report/
Cannot compute Sum('<CombinedExpression: F(quantity) * F(batch__selling_price)>'): 
'<CombinedExpression: F(quantity) * F(batch__selling_price)>' is an aggregate
```

---

## 🔍 Root Cause

Django doesn't allow nesting `Sum()` aggregations with `F()` expressions directly:

### **Problematic Code:**
```python
# This doesn't work in Django
sales_by_drug = sales.values('batch__medication__name').annotate(
    quantity=Sum('quantity'),
    revenue=Sum(F('quantity') * F('batch__selling_price')),  # ❌ Error!
    count=Count('id')
)
```

---

## ✅ Solution Implemented

### **Two-Step Approach:**

1. **First:** Annotate each record with its calculated revenue
2. **Second:** Aggregate the annotated revenue values

### **Fixed Code:**

```python
from django.db.models import ExpressionWrapper, DecimalField, F, Sum

# Step 1: Annotate revenue on individual records
sales_with_revenue = sales.annotate(
    revenue=ExpressionWrapper(
        F('quantity') * F('batch__selling_price'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )
)

# Step 2: Group and sum the pre-calculated revenue
sales_by_drug = sales_with_revenue.values('batch__medication__name').annotate(
    quantity=Sum('quantity'),
    revenue=Sum('revenue'),  # ✅ Now works!
    count=Count('id')
).order_by('-revenue')
```

---

## 🔧 Changes Made

### **File: `inventory/views.py`**

#### **1. Summary Statistics**
```python
# Annotate with ExpressionWrapper
sales_with_revenue = sales.annotate(
    revenue=ExpressionWrapper(
        F('quantity') * F('batch__selling_price'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )
)

# Aggregate the annotated values
total_revenue = sales_with_revenue.aggregate(total=Sum('revenue'))['total'] or 0
avg_sale_value = sales_with_revenue.aggregate(avg=Avg('revenue'))['avg'] or 0
```

#### **2. Sales by Medication**
```python
# Use pre-annotated revenue for grouping
sales_by_drug = sales_with_revenue.values(
    'batch__medication__name'
).annotate(
    quantity=Sum('quantity'),
    revenue=Sum('revenue'),  # Sum the pre-calculated revenue
    count=Count('id')
).order_by('-revenue')
```

#### **3. Daily Sales Trend**
```python
# Annotate date and aggregate revenue
daily_sales = sales_with_revenue.annotate(
    date=TruncDate('created_at')
).values('date').annotate(
    count=Count('id'),
    revenue=Sum('revenue')  # Sum the pre-calculated revenue
).order_by('date')
```

---

## 💡 Why This Approach is Better

### **Accuracy**
- ✅ Correctly calculates revenue for varying prices
- ✅ Each sale's revenue is calculated individually
- ✅ Prevents averaging errors

### **Performance**
- ✅ Single annotation pass
- ✅ Efficient database queries
- ✅ No subqueries needed

### **Maintainability**
- ✅ Clear two-step process
- ✅ Easy to understand
- ✅ Follows Django best practices

---

## 📊 Example Scenario

### **Consider these sales:**

| Medication | Quantity | Selling Price | Revenue |
|------------|----------|---------------|---------|
| Aspirin | 10 | UGX 500 | UGX 5,000 |
| Aspirin | 5 | UGX 600 | UGX 3,000 |

### **Old Approach (WRONG):**
```python
# Sum(quantity) * Avg(price) = 15 * 550 = 8,250 ❌
revenue = Sum('quantity') * Avg('batch__selling_price')
```

### **New Approach (CORRECT):**
```python
# Sum of individual revenues = 5,000 + 3,000 = 8,000 ✅
revenue = Sum(F('quantity') * F('batch__selling_price'))
# With ExpressionWrapper for proper execution
```

---

## ✅ Testing

### **System Check:**
```bash
python manage.py check
# Output: System check identified no issues (0 silenced).
```

### **URL Tests:**
- ✅ `/inventory/sales/report/` - Now loads without error
- ✅ Revenue calculations are accurate
- ✅ Sales by drug displays correctly
- ✅ Daily trends show proper values

---

## 🎯 Key Takeaway

**When using Django ORM with F() expressions in aggregations:**

1. ✅ **DO:** Use `ExpressionWrapper` with proper `output_field`
2. ✅ **DO:** Annotate first, then aggregate
3. ❌ **DON'T:** Nest `Sum(F() * F())` directly
4. ❌ **DON'T:** Use `Sum() * Avg()` for accurate revenue

---

## 📁 Files Modified

- ✅ `inventory/views.py` - Fixed `sales_report()` function
- ✅ `SALES_REPORT_FIX.md` - This documentation

---

## 🎉 Status: RESOLVED

The Sales Report page now works correctly with accurate revenue calculations!

**Revenue Formula:** Each sale's revenue = `quantity × batch.selling_price`  
**Aggregation:** Sum of all individual sale revenues = Total Revenue ✅
