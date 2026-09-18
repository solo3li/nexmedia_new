import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'nexmedia-super-secret-key-2026-production-ready')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = ['*'] if DEBUG else [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,web,testserver').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Core & Common
    'apps.core',
    'apps.accounts',
    'apps.billing',
    'apps.content',
    'apps.affiliate',
    'apps.support',

    # 9 AI Modular Tool Apps
    'apps.tools.tts',
    'apps.tools.stt',
    'apps.tools.text_to_video',
    'apps.tools.image_to_video',
    'apps.tools.reference_to_video',
    'apps.tools.lipsync',
    'apps.tools.motion_control',
    'apps.tools.text_to_image',
    'apps.tools.avatar_video',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'apps.core.middleware.BilingualDirectionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.nexmedia_global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database Configuration (PostgreSQL 15)
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': os.getenv('DB_NAME', 'nexmedia_db'),
        'USER': os.getenv('DB_USER', 'nexmedia'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'nexmedia_secret_password_123'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://:{os.getenv('REDIS_PASSWORD', 'nexmedia_redis_password_123')}@{os.getenv('REDIS_HOST', '127.0.0.1')}:{os.getenv('REDIS_PORT', '6379')}/1",
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

# Internationalization & Bilingual
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

# Static and Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MinIO / S3 Storage Settings
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://127.0.0.1:9000')
MINIO_PUBLIC_ENDPOINT = os.getenv('MINIO_PUBLIC_ENDPOINT', 'http://localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'nexmedia-bucket')

# Centrifugo Settings
CENTRIFUGO_API_URL = os.getenv('CENTRIFUGO_API_URL', 'http://127.0.0.1:8001/api')
CENTRIFUGO_WS_URL = os.getenv('CENTRIFUGO_WS_URL', 'ws://localhost:8001/connection/websocket')
CENTRIFUGO_API_KEY = os.getenv('CENTRIFUGO_API_KEY', 'nexmedia_centrifugo_api_key_2026')
CENTRIFUGO_SECRET = os.getenv('CENTRIFUGO_SECRET', 'nexmedia_centrifugo_secret_token_hmac_key_2026')

# Inngest Settings
INNGEST_EVENT_KEY = os.getenv('INNGEST_EVENT_KEY', 'local')
INNGEST_SIGNING_KEY = os.getenv('INNGEST_SIGNING_KEY', 'local')
INNGEST_API_URL = os.getenv('INNGEST_API_URL', 'http://127.0.0.1:8288')

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
