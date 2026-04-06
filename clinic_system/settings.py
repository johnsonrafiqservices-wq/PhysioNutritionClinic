"""
Django settings for clinic_system project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # For number formatting (intcomma, etc.)
    'crispy_forms',
    'clinic_settings',
    'crispy_bootstrap5',
    'widget_tweaks', 
    'accounts',
    'patients',
    'appointments',
    'billing',
    'medical_records',
    'reports',
    'laboratory',
    'pharmacy',
    'staff_management',
    'budget',
    'tenants',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Role-based access control middleware
    'accounts.middleware.RoleBasedAccessMiddleware',
    'accounts.middleware.DataAccessControlMiddleware',
]

ROOT_URLCONF = 'clinic_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'clinic_settings.context_processors.clinic_settings',
                'accounts.permissions.user_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'clinic_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / '',]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Role-based access control
ROLES = {
    'admin': 'Administrator',
    'doctor': 'Doctor/Physiotherapist',
    'nutritionist': 'Nutritionist',
    'receptionist': 'Receptionist',
    'nurse': 'Nurse',
    'billing': 'Billing Staff',
    'patient': 'Patient'
}

# ==================== EMAIL / SMTP SETTINGS ====================
# Configure Gmail SMTP via environment variables. Use an App Password for Gmail.
# Example env vars:
#   EMAIL_HOST_USER=youraddress@gmail.com
#   EMAIL_HOST_PASSWORD=your_gmail_app_password
#   DEFAULT_FROM_EMAIL=youraddress@gmail.com
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = (os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true')
EMAIL_USE_SSL = (os.getenv('EMAIL_USE_SSL', 'false').lower() == 'true')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'mwondhamail@gmail.com')
# IMPORTANT: Gmail App Passwords must not contain spaces. Remove spaces from the UI string.
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'uftaqjvrheuezjap')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'mwondhamail@gmail.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 20))

# Django Jet Reboot Configuration
JET_DEFAULT_THEME = 'default'
JET_THEMES = [
    {
        'theme': 'default',
        'color': '#47bac1',
        'title': 'Default'
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#ecf2f6',
        'title': 'Light Gray'
    },
   
]

# ─── Cloudinary (PDF cloud hosting for QR codes) ───────────────────────────
import cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dkop2nmv0'),
    api_key=os.environ.get('CLOUDINARY_API_KEY', '651382659514166'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'iLMXR2k16xHWLoKQHyxKovJvVew'),
    secure=True,
)
# ─────────────────────────────────────────────────────────────────────────────

# ─── Cloudflare R2 (PDF cloud hosting with public URLs) ─────────────────────
R2_ACCOUNT_ID = 'd9e56a5b8734a445352b276b3d71dd68'
R2_ACCESS_KEY_ID = 'b8522b5fef1c8f7c20165934658c570a'
R2_SECRET_ACCESS_KEY = '1596477d0a6a8cebfcf635dde045c0119fce1e9e475d01540189a17e44b61540'
R2_BUCKET_NAME = 'ndunati'
R2_ENDPOINT_URL = f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
R2_PUBLIC_URL = 'https://pub-2b1439acf6ba43be9caab27cbdd871b1.r2.dev'
# ─────────────────────────────────────────────────────────────────────────────

JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = False
# JET_INDEX_DASHBOARD = 'clinic_system.dashboard.CustomIndexDashboard'
# JET_APP_INDEX_DASHBOARD = 'clinic_system.dashboard.CustomAppIndexDashboard'

# Disable custom menu to avoid KeyError
# JET_SIDE_MENU_ITEMS will use Django Jet's default auto-generated menu
