# Development Environment URLs

## Main Application
- **Django Admin**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/
- **API Documentation**: http://localhost:8000/api/docs/
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/

## Development Tools
- **Django Debug Toolbar**: http://localhost:8000/__debug__/
- **Flower** (Celery Monitoring): http://localhost:5555
- **MailHog** (Email Testing): http://localhost:8025
- **pgAdmin** (PostgreSQL Admin): http://localhost:5050
  - Email: admin@jobboard.local
  - Password: admin123

## Backend Services
- **Elasticsearch**: http://localhost:9200
- **Redis**: redis://localhost:6379
- **PostgreSQL**: postgresql://jobboard_user:dev_password_123@localhost:5432/jobboard_dev

## How to Connect to Services

### PostgreSQL Connection
```bash
psql -h localhost -U jobboard_user -d jobboard_dev
Password: dev_password_123
```

### Redis CLI
```bash
redis-cli -h localhost -p 6379
```

### Accessing MailHog
- Web Interface: http://localhost:8025
- SMTP Server: localhost:1025 (no auth required)

## Environment Variables
Make sure to set these in your `.env` file:
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web
BASE_URL=http://localhost:8000

# Database
DB_NAME=jobboard_dev
DB_USER=jobboard_user
DB_PASSWORD=dev_password_123
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # For development
# For MailHog:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mailhog'
# EMAIL_PORT = 1025
```

## Starting the Development Environment
```bash
docker-compose up -d
```

## Stopping the Environment
```bash
docker-compose down
```

## Viewing Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f db
```
