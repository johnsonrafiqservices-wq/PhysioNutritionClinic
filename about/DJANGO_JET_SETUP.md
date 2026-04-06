# Django Jet Reboot Setup Guide

This guide explains how to set up and use Django Jet Reboot as the admin interface for the PhysioNutrition Clinic system.

## What is Django Jet Reboot?

Django Jet Reboot is a modern, responsive admin interface for Django that provides:
- Clean, modern UI design
- Responsive layout for mobile and desktop
- Customizable themes and colors
- Enhanced dashboard with widgets
- Better navigation and user experience
- Improved form layouts and field organization

## Installation Steps

### 1. Automatic Setup (Recommended)

Run the setup script from the project root directory:

```bash
python setup_jet_reboot.py
```

This script will:
- Install the required packages
- Collect static files
- Run necessary migrations
- Provide next steps

### 2. Manual Setup

If you prefer manual installation:

1. **Install Django Jet Reboot:**
   ```bash
   pip install django-jet-reboot==1.3.7
   ```

2. **Collect Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run Migrations:**
   ```bash
   python manage.py migrate jet
   python manage.py migrate dashboard
   python manage.py migrate
   ```

## Configuration

### Settings Configuration

The following settings have been configured in `clinic_system/settings.py`:

```python
INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    # ... other apps
]

# Django Jet Reboot Configuration
JET_DEFAULT_THEME = 'default'
JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = True
JET_INDEX_DASHBOARD = 'clinic_system.dashboard.CustomIndexDashboard'
JET_APP_INDEX_DASHBOARD = 'clinic_system.dashboard.CustomAppIndexDashboard'
```

### URL Configuration

Django Jet URLs have been added to `clinic_system/urls.py`:

```python
urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    # ... other URLs
]
```

### Custom Dashboard

A custom dashboard has been created in `clinic_system/dashboard.py` with:
- Clinic-specific quick actions
- Recent activity module
- Organized model lists by functionality
- System status information

## Features

### Available Themes

- **Default** - Teal theme
- **Green** - Green theme
- **Light Green** - Light green theme
- **Light Violet** - Purple theme
- **Light Blue** - Blue theme
- **Light Gray** - Dark theme

### Dashboard Modules

1. **Clinic Quick Actions**
   - Add New Patient
   - Schedule Appointment
   - Create Invoice
   - Lab Test Request

2. **Recent Actions**
   - Shows recent admin activities

3. **Organized Model Lists**
   - Patient Management
   - Appointments & Billing
   - Medical Records & Laboratory
   - System Management

### Menu Organization

The sidebar menu is organized into logical sections:
- Clinic Management
- User Management
- Patient Management
- Appointments
- Billing & Finance
- Medical Records
- Laboratory
- Inventory
- Reports

## Usage

### Accessing the Admin Interface

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Visit: `http://127.0.0.1:8000/admin/`

3. Log in with your admin credentials

### Customizing Themes

1. Log into the admin interface
2. Click on your username in the top right
3. Select "Change theme"
4. Choose from available themes
5. The theme will be saved for your user account

### Dashboard Customization

To customize the dashboard:

1. Edit `clinic_system/dashboard.py`
2. Modify the `CustomIndexDashboard` class
3. Add, remove, or rearrange modules
4. Restart the server to see changes

### Adding Custom Modules

You can add custom dashboard modules:

```python
# In clinic_system/dashboard.py
self.available_children.append(modules.LinkList(
    _('Custom Links'),
    children=[
        {
            'title': _('Custom Action'),
            'url': '/custom/url/',
            'external': False,
        },
    ],
    column=0,
    order=0
))
```

## Troubleshooting

### Common Issues

1. **Static files not loading:**
   ```bash
   python manage.py collectstatic --clear
   ```

2. **Migration errors:**
   ```bash
   python manage.py migrate jet --fake-initial
   python manage.py migrate dashboard --fake-initial
   ```

3. **Theme not applying:**
   - Clear browser cache
   - Check that static files are served correctly
   - Verify STATIC_URL and STATIC_ROOT settings

### Performance Optimization

For production environments:

1. **Enable caching:**
   ```python
   # In settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

2. **Optimize database queries:**
   - Use `select_related()` and `prefetch_related()` in admin list views
   - Add database indexes for frequently filtered fields

3. **Static file optimization:**
   - Use a CDN for static files in production
   - Enable gzip compression
   - Set appropriate cache headers

## Customization Options

### Admin Site Branding

Customize the admin site branding in your app's admin.py:

```python
from django.contrib import admin

admin.site.site_header = 'Your Clinic Name'
admin.site.site_title = 'Clinic Admin'
admin.site.index_title = 'Welcome to Your Clinic Administration'
```

### Custom CSS and JavaScript

Add custom styling by creating:
- `static/admin/css/custom.css`
- `static/admin/js/custom.js`

Then reference them in your admin classes:

```python
class CustomAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }
        js = ('admin/js/custom.js',)
```

## Support and Documentation

- **Django Jet Reboot Documentation:** [GitHub Repository](https://github.com/assem-ch/django-jet-reboot)
- **Django Admin Documentation:** [Django Docs](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- **Dashboard Customization:** See `clinic_system/dashboard.py` for examples

## Migration from Other Admin Interfaces

If migrating from Django Jazzmin or other admin interfaces:

1. Remove the old admin package from `INSTALLED_APPS`
2. Remove old admin configuration settings
3. Run migrations to clean up any old admin tables
4. Follow the installation steps above

The Django Jet Reboot interface provides a modern, professional look that's perfect for medical clinic management systems.
