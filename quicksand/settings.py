"""
Django settings for quicksand project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import sys
import logging.config
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from quicksand_common.environment import EnvironmentChecker
from django.utils.translation import gettext_lazy as _

LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
})

logger = logging.getLogger(__name__)

load_dotenv(verbose=True, dotenv_path=find_dotenv())

ENVIRONMENT = os.environ.get('ENVIRONMENT')

if not ENVIRONMENT:
    if 'test' in sys.argv:
        logger.info('No ENVIRONMENT variable found but test detected. Setting ENVIRONMENT=TEST_VALUE')
        ENVIRONMENT = EnvironmentChecker.TEST_VALUE
    else:
        raise NameError('ENVIRONMENT environment variable is required')

environment_checker = EnvironmentChecker(environment_value=ENVIRONMENT)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise NameError('SECRET_KEY environment variable is required')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environment_checker.is_debug()
IS_PRODUCTION = environment_checker.is_production()
IS_BUILD = environment_checker.is_build()
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS')

if IS_PRODUCTION:
    if not ALLOWED_HOSTS:
        raise NameError('ALLOWED_HOSTS environment variable is required when running on a production environment')
    ALLOWED_HOSTS = [allowed_host.strip() for allowed_host in ALLOWED_HOSTS.split(',')]
else:
    if ALLOWED_HOSTS:
        logger.info('ALLOWED_HOSTS environment variable ignored.')
    ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'quicksand',
    'quicksand_common',
    'quicksand_auth',
    'quicksand_invitations',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'video_encoding'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quicksand.urls'

AUTH_USER_MODEL = 'quicksand_auth.User'

JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'quicksand.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if IS_BUILD or TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DB_NAME = os.environ.get('DB_NAME')
    USERNAME = os.environ.get('USERNAME')
    PASSWORD = os.environ.get('PASSWORD')
    PORT = os.environ.get('PORT')
    HOSTNAME = os.environ.get('HOSTNAME')

    HOSTNAME_WRITER = os.environ.get('HOSTNAME_WRITER', HOSTNAME)
    HOSTNAME_READER = os.environ.get('HOSTNAME_READER', HOSTNAME_WRITER)
    db_options = {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4'
    }

    writer_db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': USERNAME,
        'PASSWORD': PASSWORD,
        'HOST': HOSTNAME_WRITER,
        'PORT': PORT,
        'OPTIONS': db_options,
    }

    DATABASES = {
        'default': writer_db_config,
        'Reader': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_NAME,
            'USER': USERNAME,
            'PASSWORD': PASSWORD,
            'HOST': HOSTNAME_READER,
            'PORT': PORT,
            'OPTIONS': db_options,
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

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_THROTTLE_RATES': {
        'link_preview': '300/hour',
    }
}

EMAIL_HOST = os.environ.get('EMAIL_HOST')

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGES = [
    ('en', _('English')),
    ('de', _('German')),
    ('tr', _('Turkish'))
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', './media')

MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'quicksand/static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

VIDEO_ENCODING_FORMATS = {
    'FFmpeg': [
        {
            'name': 'mp4_sd',
            'extension': 'mp4',
            'params': [
                '-codec:v', 'libx264', '-crf', '20', '-preset', 'medium',
                '-b:v', '1000k', '-maxrate', '1000k', '-bufsize', '2000k',
                '-vf', 'scale=-2:480',  # http://superuser.com/a/776254
                '-codec:a', 'aac', '-b:a', '128k', '-strict', '-2', '-preset', 'veryfast'
            ],
        },
    ]
}

USERNAME_MAX_LENGTH = 30
PROFILE_NAME_MAX_LENGTH = 192
PASSWORD_MIN_LENGTH = 10
PASSWORD_MAX_LENGTH = 100
PROFILE_AVATAR_MAX_SIZE = int(os.environ.get('PROFILE_AVATAR_MAX_SIZE', '10485760'))
PROFILE_COVER_MAX_SIZE = int(os.environ.get('PROFILE_COVER_MAX_SIZE', '10485760'))
