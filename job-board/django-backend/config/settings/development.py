from .base import *
import os

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost, 127.0.0.1").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "jobboard_dev"),
        "USER": os.getenv("DB_USER", "jobboard_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "dev_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Redis / Celery
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Optional dev CORS/security
CORS_ALLOW_ALL_ORIGINS = True
