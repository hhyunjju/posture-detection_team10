"""
Django settings for team10 project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
#C:\Users\user\TEAM10\team10\team10(project name)(==root dir)
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-d3%fqx+8ydlnincci)=7g4*@h2$jm5yjcs5le+=!7=qz*omdul"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "main",
    "brd",
    "home",
    "service",
    "chatbot",
    'django.contrib.sites', #추가
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.naver',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.BlockedMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "team10.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, 'templates'),
            ],
            # BASE_DIR : "C:\Users\user\aivle\bp\main\team10\templates"
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "team10.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/



STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# BASE_DIR : ../team10/
# STATIC_ROOT : ../team10/static/
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
#사용자가 업로드한 미디어 파일에 접근할 때 사용되는 URL 경로
MEDIA_URL = '/media/'
#미디어 파일들이 실제로 저장되는 서버 상의 디렉토리 경로
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

# MODEL_DIR = os.path.join(BASE_DIR, 'signlanguage/model')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# settings.py

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 3

# allauth 관련 추가 설정 (옵션)
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional' #이메일 주소 인증 선택적사항으로 설정

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile', 
            'email', #저는 email 주소 정보도 받아오고 싶어서 추가해줬습니다
        ],
        'AUTH_PARAMS': {
            'access_type': 'online'
        }
    }
}


# 허용 파일 형식
ALLOWED_FILE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
]