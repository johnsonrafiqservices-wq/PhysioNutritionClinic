# 💊 Pharmacy System - Quick Reference Guide

**Last Updated:** November 3, 2025

---

## 🎯 **What Changed?**

The system has been **consolidated** to use the **Pharmacy App** as the single source for all pharmaceutical operations, including **sales**.

### **Important:**
- ✅ **Use Pharmacy App** for everything
- ❌ **Don't use Inventory App** for new operations
- 🔗 **Sales** now accessed through Pharmacy menu

---

## 🚀 **Quick Access**

### **Main Dashboards**

| Feature | URL | Description |
|---------|-----|-------------|
| **Pharmacy Dashboard** | `/pharmacy/inventory/dashboard/` | Main pharmacy overview |
| **Sales Dashboard** | `/pharmacy/sales/` | Sales & revenue analytics |

### **Common Tasks**

| Task | Where to Go | Quick Link |
|------|-------------|------------|
| 💊 **Record a Sale** | Sales Dashboard → Record Sale button | `pharmacy:sales_dashboard` |
| 📋 **View All Sales** | Sales Dashboard → View All Sales | `pharmacy:sales_list` |
| 📊 **Sales Report** | Sales Dashboard → Sales Report | `pharmacy:sales_report` |
| 💊 **Add Medication** | Pharmacy Dashboard → Medications | `pharmacy:medication_list` |
| 📦 **Add Batch** | Pharmacy Dashboard → Batches | `pharmacy:batch_list` |
| 🚨 **Check Expiry Alerts** | Sales Dashboard → Expiry Alerts | `pharmacy:expiry_alerts` |
| 📉 **Check Low Stock** | Sales Dashboard → Low Stock Alerts | `pharmacy:low_stock_alerts` |
| 👥 **Manage Suppliers** | Sales Dashboard → Suppliers | `pharmacy:supplier_list` |
| 📝 **View Prescriptions** | Sales Dashboard → Prescriptions | `pharmacy:prescription_list` |

---

## 🎨 **Navigation Menu**

### **Top Menu Bar**

```
Home > Patients > Appointments > Pharmacy > Sales > Reports
                                    ↑          ↑
                                  Main    Sales Hub
                                Dashboard
```

### **Sales Dashboard Quick Actions**

The Sales Dashboard has **14 organized buttons** in 4 categories:

#### **1. 💰 Sales Management**
- 🆕 Record Sale (Modal)
- 📋 View All Sales
- 📊 Sales Report

#### **2. 📦 Inventory Management**
- 🏥 Pharmacy Dashboard
- 💊 Medications
- 📦 Batches
- 🔄 Stock Movements
- 📋 Stock Report

#### **3. ⚙️ Operations**
- 📝 Prescriptions
- 🚚 Suppliers
- 🛒 Purchase Orders

#### **4. 📈 Alerts & Analytics**
- ⚠️ Expiry Alerts
- 📉 Low Stock Alerts
- 📊 Analytics

---

## 📊 **Sales Workflow**

### **Recording a Sale (3 Steps)**

1. **Open Sales Dashboard**
   - Click "Sales" in top menu
   - OR go to `/pharmacy/sales/`

2. **Click "Record Sale" Button**
   - Select medication and batch
   - Enter quantity
   - Add customer name (optional)
   - Add notes (optional)

3. **Submit**
   - Sale recorded instantly
   - Stock automatically updated
   - Revenue tracked

### **Viewing Sales**

**Option 1: Sales List**
- View all sales with filters
- Search by medication, customer, date
- Export to Excel/PDF

**Option 2: Sales Report**
- Analytics and trends
- Revenue by medication
- Daily/weekly/monthly breakdowns
- Charts and visualizations

---

## 💊 **Medication Management**

### **Adding a New Medication**

1. **Go to Medications List**
   - Sales Dashboard → Medications
   - OR Pharmacy Dashboard → Medications

2. **Click "Add Medication"**
   - Fill in details:
     - Name & Generic Name
     - Category
     - Strength & Form
     - Unit Price
     - Reorder Level
     - Storage Instructions

3. **Save**
   - Medication created
   - Ready for batch addition

### **Adding a Batch**

1. **Go to Batches List**
   - Sales Dashboard → Batches

2. **Click "Add Batch"**
   - Select medication
   - Enter:
     - Batch number
     - Quantity
     - Cost & Selling Price
     - Expiry date
     - Supplier
     - Invoice number

3. **Save**
   - Batch created
   - Stock available for sales

---

## 🚨 **Alerts & Monitoring**

### **Expiry Alerts**

**Purpose:** Track medications expiring soon

**Access:** Sales Dashboard → Expiry Alerts

**What You See:**
- Medications expiring in next 90 days
- Days until expiry
- Current stock quantity
- Batch numbers

**Action:** Order replacements or plan discounts

### **Low Stock Alerts**

**Purpose:** Monitor stock levels

**Access:** Sales Dashboard → Low Stock Alerts

**What You See:**
- Medications below reorder level
- Current stock vs reorder level
- Medication details

**Action:** Create purchase orders

---

## 📋 **Prescription Management**

### **Viewing Prescriptions**

**Access:** Sales Dashboard → Prescriptions

**Features:**
- Pending prescriptions
- Dispensed prescriptions
- Search by patient

### **Dispensing a Prescription**

1. **Find Prescription**
   - Search by patient name or prescription number

2. **Click "Dispense"**
   - System checks stock availability
   - Automatically deducts from stock

3. **Print Label**
   - Prescription details
   - Dosage instructions
   - Patient information

---

## 👥 **Supplier Management**

### **Adding a Supplier**

**Access:** Sales Dashboard → Suppliers

**Required Info:**
- Supplier name
- Contact person
- Email & Phone
- Address

### **Managing Purchase Orders**

**Access:** Sales Dashboard → Purchase Orders

**Features:**
- Create new orders
- Track order status
- Mark as received
- Auto-update stock

---

## 📊 **Reports & Analytics**

### **Sales Report**

**Access:** Sales Dashboard → Sales Report

**Includes:**
- Total revenue
- Sales by medication
- Sales trends (daily/weekly/monthly)
- Top-selling medications
- Revenue charts

### **Stock Report**

**Access:** Sales Dashboard → Stock Report

**Includes:**
- Current stock levels
- Stock value
- Movement history
- Reorder recommendations

### **Analytics Dashboard**

**Access:** Sales Dashboard → Analytics

**Includes:**
- Comprehensive pharmacy analytics
- Financial overview
- Performance metrics
- Trend analysis

---

## 🔍 **Search & Filters**

### **Sales List Filters**
- Date range
- Medication name
- Customer name
- Minimum/Maximum amount

### **Medication List Filters**
- Category
- Form (tablet, capsule, etc.)
- Active/Inactive
- Low stock only

### **Batch List Filters**
- Medication
- Expiring soon
- Active/Expired
- Supplier

---

## ⚡ **Keyboard Shortcuts**

| Action | Shortcut |
|--------|----------|
| Record Sale | `Alt + R` |
| Search Medications | `Ctrl + K` |
| Refresh Dashboard | `F5` |

---

## 🆘 **Common Issues**

### **"Cannot record sale"**
✅ **Check:**
- Is batch active?
- Is stock available?
- Is batch expired?

### **"Medication not found"**
✅ **Check:**
- Has medication been created?
- Is medication active?
- Is there an active batch?

### **"Sale not appearing in list"**
✅ **Check:**
- Date filters
- Refresh page
- Check Sales Dashboard metrics

---

## 📞 **Quick Links**

| Page | URL |
|------|-----|
| Pharmacy Dashboard | `http://172.16.61.154:8000/pharmacy/inventory/dashboard/` |
| Sales Dashboard | `http://172.16.61.154:8000/pharmacy/sales/` |
| Medications | `http://172.16.61.154:8000/pharmacy/medications/` |
| Batches | `http://172.16.61.154:8000/pharmacy/batches/` |
| Sales List | `http://172.16.61.154:8000/pharmacy/sales/list/` |
| Sales Report | `http://172.16.61.154:8000/pharmacy/sales/report/` |

---

## ⚠️ **IMPORTANT NOTES**

### **DO NOT USE:**
- ❌ Old "Inventory" app for sales
- ❌ Old "inventory:sales_dashboard" URL
- ❌ Any inventory app features for new operations

### **ALWAYS USE:**
- ✅ Pharmacy app for all operations
- ✅ Sales Dashboard as your main hub
- ✅ Organized quick actions

---

## 💡 **Pro Tips**

1. **Bookmark Sales Dashboard** for quick access
2. **Check alerts daily** to prevent stockouts and expiry
3. **Use filters** to find sales quickly
4. **Review reports weekly** for insights
5. **Keep batch information updated** for accurate tracking

---

## 🎓 **Training Resources**

### **Video Tutorials** (Coming Soon)
- Recording your first sale
- Managing medication batches
- Understanding the sales report
- Handling expiry alerts

### **Documentation**
- `INVENTORY_PHARMACY_CONSOLIDATION.md` - System architecture
- `SALES_DASHBOARD_INTEGRATION.md` - Dashboard features
- This guide - Quick reference

---

**Need Help?** Contact your system administrator or check the full documentation in the project files.

---

**🎉 You're all set! The new consolidated system is easier to use and more powerful!**
