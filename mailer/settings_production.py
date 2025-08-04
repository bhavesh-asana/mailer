"""
Production settings for mailer project.
This file should be used in production environments.
"""

from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security settings for production
ALLOWED_HOSTS = [
    os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []
]

# CORS Settings - Restrictive for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    os.getenv('FRONTEND_URL', 'https://yourdomain.com'),
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Database configuration for production
if os.getenv('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }

# Static files configuration for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files configuration for production
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# CKEditor 5 Security Configuration (Production)
# Override development settings with more restrictive rules
CKEDITOR_5_CONFIGS.update({
    'email_template': {
        'toolbar': [
            'bold', 'italic', 'underline', '|',
            'link', '|',
            'bulletedList', 'numberedList', '|',
            'alignment:left', 'alignment:center', 'alignment:right', '|',
            'fontColor', '|',
            'removeFormat', '|',
            'undo', 'redo'
        ],
        'height': 400,
        'width': '100%',
        'removePlugins': ['MediaEmbed', 'EasyImage', 'CKFinder', 'ImageUpload', 'Table', 'HorizontalLine', 'SpecialCharacters'],
        'htmlSupport': {
            'allow': [
                {'name': 'a', 'attributes': {'href': True}},
                {'name': 'span', 'styles': {'color': True}},
                {'name': 'p', 'styles': {'text-align': True}},
                {'name': 'strong'},
                {'name': 'em'},
                {'name': 'u'},
            ],
            'disallow': [
                {'name': 'script'},
                {'name': 'iframe'},
                {'name': 'object'},
                {'name': 'embed'},
                {'name': 'form'},
                {'name': 'input'},
                {'name': 'img'},
                {'name': 'table'},
            ]
        }
    }
})

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'email_api': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
