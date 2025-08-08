from .base import *  # Import base settings
import os

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web', '0.0.0.0']

# Additional installed apps for development
INSTALLED_APPS += [
    'django_extensions',
    'django_celery_beat',
    'django_celery_results',
    'corsheaders',
    'django_filters',
]

# Development middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
] + MIDDLEWARE

# Internal IPs for development
INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0']

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

CORS_ALLOW_ALL_ORIGINS = True  # Only for development

# Celery settings
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Channels settings (for WebSocket support)
try:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [(os.getenv('REDIS_HOST', 'redis'), int(os.getenv('REDIS_PORT', 6379)))],
            },
        },
    }
except ImportError:
    # channels_redis not installed
    pass

# Elasticsearch settings
try:
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': os.getenv('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
        },
    }
except ImportError:
    # elasticsearch-dsl not installed
    pass

# Static and media files for development
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Logging configuration for development
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
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}