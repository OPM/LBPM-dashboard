"""
Django settings for RockSimPortal project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_REDIRECT_URL = '/project/new/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ax08!2-(*x@9i&n4vn3wcw2opzfd3vm6+xpx^x6ht&%b7gkt=('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

#AUTH_USER_MODEL = "upload.MyUser"

# Application definition

INSTALLED_APPS = [
    'LBPM.apps.LbpmConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The Django sites framework is required
    #'django.contrib.sites',
    #'impersonate',
    'bootstrap3',

    'upload',
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

ROOT_URLCONF = 'RockSimPortal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'RockSimPortal', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                #'allauth.account.context_processors.account',
                #'allauth.socialaccount.context_processors.socialaccount',
            ],
        },
    },    
]

WSGI_APPLICATION = 'RockSimPortal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


MULTIUPLOADER_FORMS_SETTINGS = {
'default': {
    'FILE_TYPES' : ["txt","zip","jpg","jpeg","flv","png","raw"],
    'CONTENT_TYPES' : [
            'image/jpeg',
            'image/png',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.presentation',
            'text/plain',
            'text/rtf',
                ],
    'MAX_FILE_SIZE': 104857634350,
    'MAX_FILE_NUMBER':50,
    'AUTO_UPLOAD': True,
},
'images':{
    'FILE_TYPES' : ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'tiff', 'ico' ],
    'CONTENT_TYPES' : [
        'image/gif',
        'image/jpeg',
        'image/pjpeg',
        'image/png',
        'image/svg+xml',
        'image/tiff',
        'image/vnd.microsoft.icon',
        'image/vnd.wap.wbmp',
        ],
    'MAX_FILE_SIZE': 10485760,
    'MAX_FILE_NUMBER':50,
    'AUTO_UPLOAD': True,
},
'video':{
    'FILE_TYPES' : ['flv', 'mpg', 'mpeg', 'mp4' ,'avi', 'mkv', 'ogg', 'wmv', 'mov', 'webm' ],
    'CONTENT_TYPES' : [
        'video/mpeg',
        'video/mp4',
        'video/ogg',
        'video/quicktime',
        'video/webm',
        'video/x-ms-wmv',
        'video/x-flv',
        ],
    'MAX_FILE_SIZE': 10485760,
    'MAX_FILE_NUMBER':50,
    'AUTO_UPLOAD': True,
},
'audio':{
    'FILE_TYPES' : ['mp3', 'mp4', 'ogg', 'wma', 'wax', 'wav', 'webm' ],
    'CONTENT_TYPES' : [
        'audio/basic',
        'audio/L24',
        'audio/mp4',
        'audio/mpeg',
        'audio/ogg',
        'audio/vorbis',
        'audio/x-ms-wma',
        'audio/x-ms-wax',
        'audio/vnd.rn-realaudio',
        'audio/vnd.wave',
        'audio/webm'
        ],
    'MAX_FILE_SIZE': 10485760,
    'MAX_FILE_NUMBER':50,
    'AUTO_UPLOAD': True,
}}

MULTIUPLOADER_FILES_FOLDER = "/tmp/petroleum"
MULTIUPLOADER_FILE_EXPIRATION_TIME = 3600


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'RockSimPortal', 'static'),
    )

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
