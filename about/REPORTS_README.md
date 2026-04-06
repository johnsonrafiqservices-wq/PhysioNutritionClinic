# Reports App - Comprehensive Documentation

## Overview

The Reports app provides a complete reporting and analytics solution for the Physio & Nutrition Clinic management system. It includes professional report generation, audit trails, scheduled reporting, and export capabilities.

## Features

### ✅ Core Features Implemented

1. **Professional Report Generation**
   - Dashboard analytics with key metrics
   - Patient demographics and statistics
   - Financial reports with revenue analysis
   - Appointment analytics and provider workload

2. **Export Capabilities**
   - PDF exports with professional formatting
   - Excel exports with charts and styling
   - CSV exports for data analysis
   - Automatic file management and cleanup

3. **Audit Trail System**
   - Complete tracking of report access and generation
   - User activity monitoring
   - Performance metrics collection
   - Error logging and debugging

4. **Scheduled Reports**
   - Automated report generation
   - Email delivery system
   - Configurable schedules (daily, weekly, monthly, quarterly)
   - Failure handling and retry logic

5. **Performance Optimization**
   - Intelligent caching system
   - Cache warming for frequently accessed reports
   - Automatic cache invalidation
   - Performance monitoring and metrics

6. **Admin Interface**
   - Complete Django admin integration
   - Report configuration management
   - Audit log viewing and filtering
   - Scheduled report management

## Installation and Setup

### 1. Install Dependencies

```bash
pip install -r reports_requirements.txt
```

### 2. Database Migration

```bash
python manage.py makemigrations reports
python manage.py migrate
```

### 3. Configure Settings

Add to your `settings.py`:

```python
# Add reports to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'reports',
]

# Cache configuration (recommended)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Email configuration for scheduled reports
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'reports@yourdomain.com'
```

### 4. URL Configuration

Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('reports/', include('reports.urls')),
]
```

## Usage Guide

### Accessing Reports

1. **Dashboard**: `/reports/` - Main analytics dashboard
2. **Patient Reports**: `/reports/patients/` - Patient demographics and statistics
3. **Financial Reports**: `/reports/financial/` - Revenue and billing analytics
4. **Appointment Reports**: `/reports/appointments/` - Appointment analytics
5. **Audit Log**: `/reports/audit/` - System audit trail
6. **Performance Metrics**: `/reports/performance/` - System performance monitoring

### Exporting Reports

All reports support three export formats:

- **PDF**: Professional formatted reports suitable for printing
- **Excel**: Spreadsheets with data and charts for analysis
- **CSV**: Raw data for custom analysis

To export a report:
1. Navigate to any report page
2. Click the "Export" dropdown button
3. Select your desired format
4. The file will be automatically downloaded

### Scheduled Reports

#### Creating Scheduled Reports

1. Access Django Admin: `/admin/`
2. Go to "Reports" → "Report configurations"
3. Create a new configuration:
   - Set report type and parameters
   - Enable scheduling
   - Set frequency (daily, weekly, monthly, quarterly)
4. Go to "Scheduled reports" and create a schedule:
   - Link to your configuration
   - Add recipient email addresses
   - Set next run time

#### Running Scheduled Reports

Use the management command:

```bash
# Run all due scheduled reports
python manage.py run_scheduled_reports

# Dry run to see what would be sent
python manage.py run_scheduled_reports --dry-run

# Force run all active reports
python manage.py run_scheduled_reports --force
```

#### Setting up Automated Scheduling

Add to your crontab or task scheduler:

```bash
# Run every hour
0 * * * * /path/to/python /path/to/manage.py run_scheduled_reports

# Run daily at 6 AM
0 6 * * * /path/to/python /path/to/manage.py run_scheduled_reports
```

### Performance Optimization

#### Cache Management

The reports app includes intelligent caching:

```python
from reports.cache import ReportCache, CacheWarmer

# Warm caches for better performance
CacheWarmer.warm_all_caches()

# Get cache statistics
stats = ReportCache.get_cache_stats()

# Invalidate specific report cache
ReportCache.invalidate_report_cache('financial')
```

#### Cache Warming

Set up cache warming in your deployment:

```python
# In your Django management command or deployment script
from reports.cache import CacheWarmer
CacheWarmer.warm_all_caches()
```

## API Reference

### Models

#### ReportConfiguration
- Stores custom report configurations
- Supports JSON parameters for flexible filtering
- Links to user who created the configuration

#### ReportAuditLog
- Tracks all report generation and access
- Records performance metrics
- Stores user information and IP addresses

#### ScheduledReport
- Manages automated report delivery
- Handles failure tracking and retry logic
- Supports multiple recipients

#### ReportExport
- Tracks exported files
- Manages file expiration
- Records download statistics

### Views

#### reports_dashboard(request)
Main analytics dashboard with key metrics and charts.

#### patient_reports(request)
Patient demographics and statistics with filtering options.

#### financial_reports(request)
Financial analytics including revenue, payments, and aging reports.

#### appointment_report(request)
Appointment analytics with provider workload and service popularity.

#### export_report(request)
Handles report exports in PDF, Excel, and CSV formats.

#### audit_log(request)
Displays audit trail with filtering and pagination.

#### report_performance(request)
Shows system performance metrics and optimization recommendations.

### Utilities

#### PDFReportGenerator
Professional PDF generation with:
- Custom styling and branding
- Tables with formatting
- Charts and graphs
- Summary statistics

#### ExcelReportGenerator
Excel generation with:
- Multiple worksheets
- Charts and graphs
- Professional styling
- Data validation

#### ReportAuditMixin
Mixin for adding audit logging to views:
- Automatic activity tracking
- Performance measurement
- Error logging

## Customization

### Adding New Report Types

1. Create export data generator:

```python
def generate_custom_export_data(parameters):
    # Your custom data logic here
    return {
        'summary_stats': {...},
        'tables': [...]
    }
```

2. Add to export view:

```python
elif report_type == 'custom':
    content_data = generate_custom_export_data(parameters)
```

3. Create template and add navigation links

### Custom Report Templates

Create custom templates in `templates/reports/`:
- Follow existing template structure
- Include export functionality
- Add audit logging
- Implement caching if needed

### Extending Audit Logging

Add custom audit events:

```python
from reports.utils import ReportAuditMixin

class MyView(ReportAuditMixin, View):
    def get(self, request):
        # Your view logic
        
        self.log_report_activity(
            request=request,
            report_type='custom',
            report_name='My Custom Report',
            action='viewed',
            # ... other parameters
        )
```

## Troubleshooting

### Common Issues

1. **Export Fails**
   - Check file permissions in media directory
   - Verify reportlab and openpyxl are installed
   - Check error logs in audit trail

2. **Scheduled Reports Not Sending**
   - Verify email configuration
   - Check scheduled report status in admin
   - Run management command manually to test

3. **Performance Issues**
   - Enable caching (Redis recommended)
   - Warm caches after deployment
   - Check database indexes on date fields

4. **Cache Issues**
   - Verify Redis connection
   - Check cache timeout settings
   - Monitor cache hit rates

### Debug Mode

Enable debug logging in settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'reports.log',
        },
    },
    'loggers': {
        'reports': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Security Considerations

1. **Access Control**
   - All views require login (`@login_required`)
   - Consider adding role-based permissions
   - Audit all report access

2. **Data Privacy**
   - Export files are automatically cleaned up
   - Audit logs track all data access
   - Consider data anonymization for exports

3. **Email Security**
   - Use TLS for email delivery
   - Validate recipient addresses
   - Consider encryption for sensitive reports

## Performance Benchmarks

Typical performance metrics:
- Dashboard generation: 0.5-2 seconds
- PDF export: 1-3 seconds
- Excel export: 2-5 seconds
- Cached reports: 0.1-0.3 seconds

## Support and Maintenance

### Regular Maintenance Tasks

1. **Clean up old audit logs** (recommended monthly):
```bash
python manage.py shell -c "
from reports.models import ReportAuditLog
from django.utils import timezone
from datetime import timedelta
cutoff = timezone.now() - timedelta(days=90)
ReportAuditLog.objects.filter(timestamp__lt=cutoff).delete()
"
```

2. **Clean up expired exports** (recommended weekly):
```bash
python manage.py shell -c "
from reports.models import ReportExport
from django.utils import timezone
ReportExport.objects.filter(expires_at__lt=timezone.now()).delete()
"
```

3. **Monitor cache performance**:
```bash
python manage.py shell -c "
from reports.cache import ReportCache
print(ReportCache.get_cache_stats())
"
```

### Monitoring

Key metrics to monitor:
- Report generation times
- Cache hit rates
- Export success rates
- Scheduled report delivery success
- Database query performance

## Contributing

When adding new features:
1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Include audit logging
5. Consider caching implications
6. Test export functionality

## License

This reports app is part of the Physio & Nutrition Clinic management system.
