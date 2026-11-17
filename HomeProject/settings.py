"""
Django settings for HomeProject project.
"""

import os
from pathlib import Path
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-5!it^xv2)&n*fsz$80yu@uh_+88v4)35%*&er)+=(*9qk)8fq2'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_jalali',   # ← اضافه شد
    'accounts.apps.AccountsConfig',
    'properties.apps.PropertiesConfig',
    'agencies.apps.AgenciesConfig',
    'support.apps.SupportConfig',
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

ROOT_URLCONF = 'HomeProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'HomeProject.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Email (حالت تست: چاپ در کنسول)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'دپارتمان املاک اندیشه <noreply@andisheh-estate.ir>'


# Auth

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = reverse_lazy('accounts:login')
LOGIN_REDIRECT_URL = reverse_lazy('properties:home')
LOGOUT_REDIRECT_URL = reverse_lazy('properties:home')

# ===== SMS.ir (پنل پیامکی) =====
SMS_IR_API_KEY = 'AezIDWovOaTGrl41SBedcXjYIQHUSDbvjSotCemi0f7qmTMf'  # ← از پروژه قبلی
SMS_IR_LINE_NUMBER = 30002128098440
SMS_IR_TEMPLATE_ID = 804464   # ← شناسه قالب پیامک

# مدت اعتبار OTP (ثانیه)
OTP_EXPIRY_SECONDS = 120   # ۲ دقیقه

# محدودیت درخواست OTP در ۲۴ ساعت
OTP_MAX_REQUESTS_PER_DAY = 3

