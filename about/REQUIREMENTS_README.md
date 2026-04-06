# Requirements Documentation

This document explains the different requirements files in this project and how to use them.

## 📋 Requirements Files

### 1. **requirements.txt** (Base Requirements)
The main requirements file containing all essential packages needed to run the application.

**Use this for:**
- Initial project setup
- Basic development environment
- Containerization (Docker)

**Install:**
```bash
pip install -r requirements.txt
```

### 2. **requirements-dev.txt** (Development Requirements)
Additional packages needed for development and testing.

**Includes:**
- Testing frameworks (pytest, pytest-django)
- Code coverage tools
- Faker for test data generation
- Enhanced debugging tools

**Install:**
```bash
pip install -r requirements-dev.txt
```

### 3. **requirements-prod.txt** (Production Requirements)
Optimized packages for production deployment.

**Includes:**
- Production server (Gunicorn)
- Production database drivers
- Security monitoring (Sentry)
- Static file serving
- CORS handling

**Install:**
```bash
pip install -r requirements-prod.txt
```

### 4. **requirements-full.txt** (Complete Freeze)
Full pip freeze output capturing all installed packages including dependencies.

**Use this for:**
- Exact environment replication
- Debugging dependency issues
- Reference of complete package versions

**Install:**
```bash
pip install -r requirements-full.txt
```

## 📦 Key Packages Overview

### Core Framework
- **Django 4.2.7**: Web framework
- **django-jet-reboot**: Modern admin interface

### UI & Forms
- **django-crispy-forms**: Beautiful form rendering
- **crispy-bootstrap5**: Bootstrap 5 integration
- **django-widget-tweaks**: Form field manipulation
- **django-colorfield**: Color picker field

### Reporting & Documents
- **reportlab**: PDF generation
- **weasyprint**: HTML to PDF conversion
- **xhtml2pdf**: Alternative PDF generation
- **openpyxl**: Excel file generation
- **xlsxwriter**: Advanced Excel features
- **pandas**: Data manipulation

### Barcode & QR Codes
- **python-barcode**: Barcode generation
- **qrcode**: QR code generation

### Performance
- **redis**: In-memory caching
- **django-redis**: Django cache backend
- **celery**: Background task processing

### API & REST
- **djangorestframework**: REST API framework
- **drf-yasg**: API documentation

### Security
- **PyJWT**: JSON Web Tokens
- **cryptography**: Encryption utilities

## 🚀 Quick Setup Guide

### Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install development requirements
pip install -r requirements-dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Populate laboratory tests
python manage.py populate_lab_tests

# Run development server
python manage.py runserver
```

### Production Environment
```bash
# Install production requirements
pip install -r requirements-prod.txt

# Set environment variables
# DATABASE_URL, SECRET_KEY, DEBUG=False, etc.

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn clinic_system.wsgi:application --bind 0.0.0.0:8000
```

## 🔄 Updating Requirements

### After Installing New Packages
```bash
# Update main requirements
pip freeze > requirements-full.txt

# Manually add to requirements.txt (organized by category)
# Only add direct dependencies, not sub-dependencies
```

### Checking for Updates
```bash
# List outdated packages
pip list --outdated

# Upgrade specific package
pip install --upgrade package-name

# Update requirements
pip freeze > requirements-full.txt
```

## 📊 Package Categories

### Essential (Always Needed)
- Django
- django-crispy-forms
- crispy-bootstrap5
- Pillow
- reportlab
- openpyxl

### Performance (Recommended for Production)
- redis
- django-redis
- celery
- gunicorn

### Optional (Based on Features)
- weasyprint (Advanced PDF)
- pandas (Data analysis)
- django-storages (Cloud storage)
- sentry-sdk (Error monitoring)

## ⚠️ Version Notes

### Python Version
- **Required**: Python 3.8+
- **Recommended**: Python 3.10+

### Django Version
- **Current**: Django 4.2.7 (LTS)
- **Upgrade Path**: Plan for Django 5.x when needed

### Critical Dependencies
- **redis**: Required for caching and Celery
- **Pillow**: Required for image processing
- **reportlab**: Required for PDF generation

## 🐛 Troubleshooting

### Common Issues

**1. Pillow Installation Error**
```bash
# Windows: Install Visual C++ Build Tools
# Linux: Install python3-dev and libjpeg-dev
sudo apt-get install python3-dev libjpeg-dev
```

**2. WeasyPrint Issues**
```bash
# Windows: Install GTK3 Runtime
# Linux: Install dependencies
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

**3. psycopg2 Installation Error**
```bash
# Use binary version instead
pip install psycopg2-binary
```

**4. Redis Connection Error**
```bash
# Ensure Redis server is running
# Windows: Run redis-server.exe
# Linux: sudo systemctl start redis
```

## 📝 Best Practices

1. **Always use virtual environments**
2. **Pin specific versions** in requirements.txt
3. **Test requirements** before deploying
4. **Keep requirements organized** by category
5. **Document custom packages** and reasons
6. **Update regularly** for security patches

## 🔗 Related Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Jet Reboot](https://github.com/assem-ch/django-jet-reboot)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)

## 📞 Support

For issues with specific packages, refer to their official documentation or raise an issue in the project repository.

---

**Last Updated**: November 6, 2025  
**Project**: PhysioNutrition Clinic Management System  
**Python Version**: 3.10+  
**Django Version**: 4.2.7
