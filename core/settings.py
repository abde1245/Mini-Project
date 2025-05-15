import os
from pathlib import Path

# Base directory of your project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY — replace this with a real one for production!
SECRET_KEY = 'django-insecure-your-secret-key' # Replace with your actual secret key

# Debug mode — switch to False before deploying
DEBUG = True

ALLOWED_HOSTS = [] # Add your domain/IP here for production, e.g., ['yourdomain.com', 'www.yourdomain.com']

# App definitions
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom apps
    'users.apps.UsersConfig', # Using AppConfig for better structure
    'departments.apps.DepartmentsConfig',
    'courses.apps.CoursesConfig',
    'ta_assignments.apps.TaAssignmentsConfig',
    'duties.apps.DutiesConfig',
    'duty_tracking.apps.DutyTrackingConfig',
    'student_submissions.apps.StudentSubmissionsConfig',
    'notifications.apps.NotificationsConfig',
    'reporting.apps.ReportingConfig',
]

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:dashboard_dispatch' # After login, redirect here
LOGOUT_REDIRECT_URL = 'users:login' # After logout, redirect here


# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Manages sessions across requests
    'django.middleware.common.CommonMiddleware', # Handles common tasks like adding slashes
    'django.middleware.csrf.CsrfViewMiddleware', # Cross-Site Request Forgery protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Associates users with requests using sessions
    'django.contrib.messages.middleware.MessageMiddleware', # Enables cookie- and session-based messaging
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjacking protection
]

ROOT_URLCONF = 'core.urls'

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add project-level templates directory here
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,  # Django will look for a 'templates' subdirectory in each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # Adds the request object to template context
                'django.contrib.auth.context_processors.auth',  # Adds user and perms objects
                'django.contrib.messages.context_processors.messages', # Adds messages object
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database (using SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # 'OPTIONS': { # Optional: customize minimum length
        #     'min_length': 9,
        # }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Your local time zone
USE_I18N = True # Enable internationalization
USE_TZ = True   # Enable timezone-aware datetimes

# Static files (CSS, JavaScript, Images) - for development and collection
STATIC_URL = '/static/'
# Directory where Django will look for static files in addition to app's 'static' dirs
STATICFILES_DIRS = [
    BASE_DIR / 'static', # Project-level static files
]
# Directory where `collectstatic` will gather static files for deployment
# STATIC_ROOT = BASE_DIR / 'staticfiles' # Uncomment and set for production

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Directory where user-uploaded files will be stored

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Messages framework storage
# from django.contrib.messages import constants as messages
# MESSAGE_TAGS = {
#     messages.DEBUG: 'alert-secondary',
#     messages.INFO: 'alert-info',
#     messages.SUCCESS: 'alert-success',
#     messages.WARNING: 'alert-warning',
#     messages.ERROR: 'alert-danger',
# }

# Ensure each app has an apps.py file with a corresponding AppConfig class
# e.g., users/apps.py:
# from django.apps import AppConfig
# class UsersConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'users'