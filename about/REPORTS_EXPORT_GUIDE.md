# Reports Export Functionality Guide

## Overview
Complete guide to the report generation and export system with PDF and Excel format support.

---

## Export Formats Available

### **1. PDF Export** 📄
- **Professional Layout**: Clean, medical-grade document formatting
- **Features**:
  - Custom title and subtitle styling
  - Summary statistics section
  - Professional data tables with borders
  - Page breaks for multi-page reports
  - Clinic branding and headers
  - Generated date and time stamps
- **Use Cases**: Official documentation, printing, archival

### **2. Excel Export** 📊
- **Advanced Spreadsheet**: Professional Excel workbooks with styling
- **Features**:
  - Formatted headers with colors
  - Alternating row colors for readability
  - Auto-adjusted column widths
  - Summary statistics section
  - Multiple data tables
  - Professional fonts and borders
- **Use Cases**: Data analysis, further processing, charts

### **3. CSV Export** 📋
- **Simple Data Export**: Raw tabular data
- **Features**:
  - Plain text format
  - Easy to import into other systems
  - Lightweight file size
- **Use Cases**: Data import, database loading, simple analysis

---

## Available Reports for Export

### **1. Dashboard Report**
**Export Data Includes:**
- **Summary Statistics**:
  - Total Patients
  - New Patients (in period)
  - Total Appointments
  - Completed Appointments
  - Total Revenue (UGX)
  - Report Period
- **Tables**:
  - Popular Services (Name, Category, Price, Appointment Count)

**Export URL**: `/reports/export/`
**Parameters**: `report_type=dashboard`, `start_date`, `end_date`

---

### **2. Patient Report**
**Export Data Includes:**
- **Summary Statistics**:
  - Total Patients
  - New Patients (in period)
  - Average Age
  - Report Period
- **Tables**:
  - Patient List (Name, Email, Phone, Gender, Age, Registration Date, Insurance)
  - Limited to 100 patients for performance

**Export URL**: `/reports/export/`
**Parameters**: `report_type=patient`, `date_range`, `gender`

---

### **3. Financial Report**
**Export Data Includes:**
- **Summary Statistics**:
  - Total Revenue (UGX)
  - Outstanding Amount (UGX)
  - Total Invoices
  - Report Period
- **Tables**:
  - Recent Invoices (Invoice #, Patient, Amount, Status, Created, Due Date)
  - Limited to 50 invoices

**Export URL**: `/reports/export/`
**Parameters**: `report_type=financial`, `period`

---

### **4. Appointment Report**
**Export Data Includes:**
- **Summary Statistics**:
  - Total Appointments
  - Completed Count
  - Cancelled Count
  - No Show Count
  - Report Period
- **Tables**:
  - Appointments (Date/Time, Patient, Provider, Service, Status, Notes)
  - Limited to 100 appointments

**Export URL**: `/reports/export/`
**Parameters**: `report_type=appointment`, `start_date`, `end_date`

---

## How to Export Reports

### **From Report Templates**

All report templates have export buttons in the page actions section:

```html
<div class="btn-group" role="group">
    <button type="button" class="btn btn-outline-secondary dropdown-toggle" 
            data-bs-toggle="dropdown">
        <i class="bi bi-download"></i> Export
    </button>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="#" 
               onclick="exportReport('report_type', 'pdf')">
            <i class="bi bi-file-pdf"></i> Export as PDF
        </a></li>
        <li><a class="dropdown-item" href="#" 
               onclick="exportReport('report_type', 'excel')">
            <i class="bi bi-file-excel"></i> Export as Excel
        </a></li>
    </ul>
</div>
```

### **JavaScript Export Function**

```javascript
function exportReport(reportType, format) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/reports/export/';
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Add report type
    const reportTypeInput = document.createElement('input');
    reportTypeInput.type = 'hidden';
    reportTypeInput.name = 'report_type';
    reportTypeInput.value = reportType;
    form.appendChild(reportTypeInput);
    
    // Add export format
    const formatInput = document.createElement('input');
    formatInput.type = 'hidden';
    formatInput.name = 'export_format';
    formatInput.value = format;
    form.appendChild(formatInput);
    
    // Add any filter parameters (dates, etc.)
    // ... add more inputs as needed
    
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}
```

---

## Export Process Flow

### **1. User Initiates Export**
- User clicks "Export as PDF" or "Export as Excel" button
- JavaScript creates hidden form with parameters
- Form submits to `/reports/export/` endpoint

### **2. Server Processes Request**
```python
@login_required
@require_http_methods(["POST"])
def export_report(request):
    # Get parameters
    report_type = request.POST.get('report_type')
    export_format = request.POST.get('export_format')
    
    # Generate report data
    content_data = generate_xxx_export_data(parameters)
    
    # Create export file
    response, export_record = create_report_export(
        user=request.user,
        report_type=report_type,
        export_format=export_format,
        content_data=content_data
    )
    
    # Log activity
    audit_mixin.log_report_activity(...)
    
    return response
```

### **3. File Generation**
- **PDF**: Uses ReportLab library for professional PDF generation
- **Excel**: Uses openpyxl library for advanced Excel formatting
- **CSV**: Uses Python csv module for simple data export

### **4. File Download**
- Browser receives file with appropriate headers
- File downloads automatically with timestamped filename
- Format: `ReportName_YYYYMMDD_HHMMSS.ext`

### **5. Audit Logging**
- Export activity logged in ReportAuditLog
- Tracks: user, report type, format, file size, timestamp
- Export record created in ReportExport table
- Files expire after 7 days

---

## PDF Export Details

### **Professional Features**
- **Custom Styling**: Title, subtitle, headers with custom colors
- **Page Layout**: A4 size with proper margins
- **Tables**: Professional bordered tables with data
- **Summary Stats**: Key metrics displayed prominently
- **Branding**: Clinic name and information
- **Timestamps**: Generation date and time

### **PDF Structure**
```
┌─────────────────────────────────┐
│        Report Title             │
│        Subtitle                 │
│   Generated on: Date & Time     │
├─────────────────────────────────┤
│   Summary Statistics            │
│   • Total Patients: 150         │
│   • Total Revenue: UGX 5,000,000│
│   • Report Period: ...          │
├─────────────────────────────────┤
│   Data Table Title              │
│ ┌───────┬─────────┬──────────┐ │
│ │Header1│Header2  │Header3   │ │
│ ├───────┼─────────┼──────────┤ │
│ │Data1  │Data2    │Data3     │ │
│ │Data1  │Data2    │Data3     │ │
│ └───────┴─────────┴──────────┘ │
└─────────────────────────────────┘
```

---

## Excel Export Details

### **Professional Features**
- **Styled Headers**: Blue background, white bold text
- **Alternating Rows**: Light gray for better readability
- **Borders**: Professional thin borders on all cells
- **Column Widths**: Auto-adjusted for content
- **Multiple Sheets**: Support for multiple data tables
- **Formulas**: Can include calculations if needed

### **Excel Structure**
```
Row 1:  Report Title (Large, Bold)
Row 2:  Subtitle (Medium)
Row 3:  Generated on: Date & Time (Italic)
Row 4:  [Empty]
Row 5:  Summary Statistics (Bold)
Row 6:  Total Patients: 150
Row 7:  Total Revenue: UGX 5,000,000
Row 8:  [Empty]
Row 9:  Data Table Title (Bold)
Row 10: [Headers with blue background]
Row 11+: [Data rows with alternating colors]
```

---

## Currency Formatting

All financial data is formatted in **Ugandan Shillings (UGX)**:

### **Format Examples**
- Revenue: `UGX 5,000,000` (no decimals)
- Service Price: `UGX 50,000`
- Invoice Amount: `UGX 150,000`

### **Implementation**
```python
# In export data generation
f"UGX {amount:,.0f}"  # Formats with comma separators, no decimals
```

---

## File Management

### **Export Records**
- All exports tracked in `ReportExport` model
- Fields: user, report type, format, file size, timestamp
- Automatic expiration after 7 days
- Can be viewed in admin interface

### **Audit Trail**
- Complete audit log in `ReportAuditLog` model
- Tracks: generation, viewing, exporting
- Performance metrics: execution time, record count
- Error logging for failed exports

### **File Naming Convention**
```
{ReportName}_{YYYYMMDD}_{HHMMSS}.{extension}

Examples:
- Dashboard_Report_20251022_151030.pdf
- Patient_Analytics_20251022_151045.xlsx
- Financial_Report_20251022_151100.csv
```

---

## Error Handling

### **Export Errors**
```python
try:
    # Generate export
    response, export_record = create_report_export(...)
    return response
except Exception as e:
    # Log error
    audit_mixin.log_report_activity(
        success=False,
        error_message=str(e)
    )
    return JsonResponse({'error': str(e)}, status=500)
```

### **Common Issues**
1. **Missing Data**: Returns empty tables with headers
2. **Large Datasets**: Limited to prevent timeouts (50-100 records)
3. **Invalid Parameters**: Returns 400 error with message
4. **Permission Issues**: Requires login, returns 403 if unauthorized

---

## Performance Considerations

### **Data Limits**
- **Patient Report**: Max 100 patients
- **Financial Report**: Max 50 invoices
- **Appointment Report**: Max 100 appointments
- **Dashboard**: Top 10 services

### **Optimization**
- Efficient database queries with select_related
- Pagination for large datasets
- Caching for frequently accessed reports
- Asynchronous processing for large exports (future)

---

## Security Features

### **Access Control**
- `@login_required` decorator on all export views
- User authentication required
- Audit logging of all export activities
- IP address and user agent tracking

### **Data Protection**
- Files expire after 7 days
- Secure file generation in memory
- No temporary files on disk
- CSRF protection on all POST requests

---

## Usage Examples

### **Export Dashboard Report as PDF**
```javascript
exportReport('dashboard', 'pdf');
```

### **Export Patient Report as Excel**
```javascript
exportReport('patient', 'excel');
```

### **Export Financial Report with Date Range**
```javascript
// Add date parameters to form before submit
const startDateInput = document.createElement('input');
startDateInput.type = 'hidden';
startDateInput.name = 'start_date';
startDateInput.value = '2025-01-01';
form.appendChild(startDateInput);

exportReport('financial', 'pdf');
```

---

## Admin Interface

### **View Export History**
- Navigate to: Admin → Reports → Report Exports
- Filter by: user, report type, format, date
- View: file size, download count, expiration

### **View Audit Logs**
- Navigate to: Admin → Reports → Report Audit Logs
- Filter by: user, report type, action, date
- View: execution time, success/failure, errors

---

## Future Enhancements

### **Planned Features**
- [ ] Scheduled exports via email
- [ ] Custom export templates
- [ ] Chart/graph inclusion in exports
- [ ] Batch export multiple reports
- [ ] Export to Google Sheets
- [ ] Real-time export progress indicator
- [ ] Export history dashboard
- [ ] Custom date range picker

---

## Troubleshooting

### **Export Not Working**
1. Check browser console for JavaScript errors
2. Verify CSRF token is present
3. Check server logs for Python errors
4. Ensure user is logged in
5. Verify report type parameter is correct

### **File Not Downloading**
1. Check browser download settings
2. Verify Content-Disposition header
3. Check file size (may be too large)
4. Try different browser

### **Empty Export**
1. Verify date range has data
2. Check filter parameters
3. Review database for records
4. Check query limits (50-100 records)

---

## Technical Stack

### **Backend**
- **Django**: Web framework
- **ReportLab**: PDF generation
- **openpyxl**: Excel generation
- **Python csv**: CSV export

### **Frontend**
- **JavaScript**: Export form submission
- **Bootstrap**: UI components
- **Bootstrap Icons**: Export icons

### **Database**
- **ReportExport**: Export tracking
- **ReportAuditLog**: Activity logging

---

**Last Updated**: October 22, 2025  
**Version**: 2.0.0  
**Status**: Production Ready ✅
