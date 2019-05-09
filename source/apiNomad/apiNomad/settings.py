"""
Django settings for apiNomad project.

Generated by 'django-admin startproject' using Django 1.11.18.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    'SECRET_KEY',
    default=')4dsj5ogd@u=mruvslkn&zv$1799*3po55)udj3=cut3#mbpld'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default="True", cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=lambda v: [s.strip() for s in v.split(',')],
    default=''
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_docs',
    'rest_framework.authtoken',
    'corsheaders',
    'cuser',
    'apiNomad',
    'location',
    'video',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'apiNomad.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.template.context_processors.i18n",
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'apiNomad.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apiNomad.authentication.TemporaryTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.'
                                'LimitOffsetPagination',
    'HIDE_DOCS': config('DEBUG', default='True', cast=bool),
    'PAGE_SIZE': 100,
}

# Temporary Token

REST_FRAMEWORK_TEMPORARY_TOKENS = {
    'MINUTES': 10,
    'RENEW_ON_SUCCESS': True,
    'USE_AUTHENTICATION_BACKENDS': False,
}

# Activation Token

ACTIVATION_TOKENS = {
    'MINUTES': config('ACTIVATION_TOKENS_MINUTES', default=2880),
}

# config django-username-email plugin
# default model user
AUTH_USER_MODEL = 'apiNomad.User'
CUSER = {
    'app_verbose_name': 'Authentication and Authorization',
    'register_proxy_auth_group_model': False,
}

# Email service configuration (using Anymail).
# Refer to Anymail's documentation for configuration details.

ANYMAIL = {
    "SENDINBLUE_API_KEY": config('SENDINBLUE_API_KEY', default=''),
    'TEMPLATES': {
        "CONFIRM_SIGN_UP": "example_template_id",
        "FORGOT_PASSWORD": "example_template_id",
    },
}
EMAIL_BACKEND = 'anymail.backends.sendinblue.EmailBackend'
# This 'FROM' email is not used with SendInBlue templates
DEFAULT_FROM_EMAIL = 'noreply@noreply.org'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'America/Montreal'

USE_I18N = True

USE_L10N = True

USE_TZ = True


def gettext(x): return x


LANGUAGES = (
    ('fr', gettext('French')),
    ('en', gettext('English')),
)

# Local path
LOCALE_PATHS = (
    'apiNomad/locale',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

# CORS Header Django Rest Framework

CORS_ORIGIN_ALLOW_ALL = True

# Conf for upload files
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# These settings are not related to the core API functionality. Feel free to
# edit them to your needs.
# NOTE: "{{token}}" is a placeholder for the real activation token. It will be
#       dynamically replaced by the real "token".
CONSTANT = {
    "ORGANIZATION": "UZIYA",
    "EMAIL_SERVICE": True,
    "AUTO_ACTIVATE_USER": False,
    "GROUPS_USER": {
        "PRODUCER": "producer",
        "VIEWER": "viewer",
    },
    "FRONTEND_INTEGRATION": {
        "ACTIVATION_URL": "{}/auth/register/activate/token".format(
            config('CLIENT_HOST', default='localhost:8000')
        ),
        "FORGOT_PASSWORD_URL": "{}/auth/reset-password/token".format(
            config('CLIENT_HOST', default='localhost:8000')
        ),
    },
    "VIDEO": {
        "WIDTH": 1280,
        "HEIGHT": 720,
        "SIZE": 783504130,
    },
}
