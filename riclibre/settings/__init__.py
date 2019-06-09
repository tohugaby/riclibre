"""
Django settings for riclibre project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import logging
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sentry_sdk
from celery.schedules import crontab
from django.urls import reverse
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

import riclibre

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if os.getenv('DEBUG') == 'True':
    DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
FROM_ENV_VAR_DOMAINS = [os.getenv('DOMAIN_NAME')]
try:
    FROM_ENV_VAR_DOMAINS = os.getenv('DOMAIN_NAME').split(',')
    ALLOWED_HOSTS += FROM_ENV_VAR_DOMAINS
except AttributeError as attr_err:
    pass
except Exception as exc:
    pass

MAIL_DOMAIN = os.getenv('MAIL_DOMAIN', 'riclibre.fr.nf')

INTERNAL_IPS = ['127.0.0.1', ]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'tempus_dominus',
    'debug_toolbar',
    'captcha',
    'account_manager.apps.AccountManagerConfig',
    'referendum.apps.ReferendumConfig',
    'id_card_checker.apps.IdCardCheckerConfig',  # id checker apps should always be loaded after main app: referendum
    'achievements.apps.AchievementsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'riclibre.urls'

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

WSGI_APPLICATION = 'riclibre.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER', os.getenv('DATABASE_NAME')),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT', '5432')
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
    {
        'NAME': 'referendum.validators.RequiredCharactersValidator',
    },

]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # '/var/www/static/'
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "riclibre", "static"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Authentication
AUTH_USER_MODEL = 'account_manager.CustomUser'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = '/'

# Email config
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

# Site management

SITE_ID = 1

# Logs

# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.DEBUG,  # Capture info and above as breadcrumbs
    event_level=logging.DEBUG  # Send errors as events
)

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    release=riclibre.__version__
)

if os.environ.get('ADMINS'):
    admin_list = os.environ.get('ADMINS').split(";")
    ADMINS = [(admin.split("@")[0], admin) for admin in admin_list]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },

    },
    'loggers': {
        # 'django': {
        #     'handlers': ['console'],
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        # },
        '': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        },
        'referendum': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        },
        'account_manager': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        },
        'id_card_checker': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        }
    }
}

# Google reCaptcha
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '')
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# a custom variable to desactivate recaptcha
DESACTIVATE_RECAPTCHA = False
if os.getenv('DESACTIVATE_RECAPTCHA') == 'True':
    DESACTIVATE_RECAPTCHA = True

# Task management

BROKER_URL = os.getenv('BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.getenv('BROKER_URL', 'redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Paris'
CELERY_BEAT_SCHEDULE = {
    'clean-identities': {
        'task': 'referendum.tasks.clean_identities_job',
        'schedule': crontab(minute=40, hour='*/1'),
    },
    'check-perms': {
        'task': 'referendum.tasks.remove_citizen_perm_job',
        'schedule': crontab(minute=50, hour='*/1'),
    },
    'check-cards': {
        'task': 'id_card_checker.tasks.launch_waiting_id_cards_checks',
        'schedule': crontab(minute='*/5'),
    },

}

OBSERVATIONS_LINKS = {
    'id_card_checker.models.IdCard': ['referendum.observers.id_checker_observer',
                                      'achievements.observers.achievements_observer'],
    'account_manager.models.CustomUser': ['achievements.observers.achievements_observer', ],
    'referendum.models.referendum.Referendum': ['achievements.observers.achievements_observer', ],
    'referendum.models.comment.Comment': ['achievements.observers.achievements_observer', ],
    'referendum.models.like.Like': ['achievements.observers.achievements_observer', ],
    'referendum.models.vote.VoteToken': ['achievements.observers.achievements_observer', ],
}

# Referendum config

# Number of days between referendum publication and vote start.
NB_DAYS_BEFORE_EVENT_START = 15

# id_card_checker config

ID_CARD_VALIDITY_LENGTH = 3653
MAX_ID_CARD_FILE_SIZE = 2097152
