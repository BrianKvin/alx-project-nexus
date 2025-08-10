# Job Board Platform - Docker Setup Guide

This guide covers the complete Docker setup for the Job Board Platform, including development, testing, and production environments.

## Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 4GB RAM available for containers
- 10GB+ free disk space

### Installation Commands

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install docker.io docker-compose-plugin

# macOS (using Homebrew)
brew install docker docker-compose

# Windows
# Download Docker Desktop from https://docker.com/desktop

# Check docker verion
docker --version

# check if docker is running
docker info

# Start docker if not running
sudo systemctl start docker

# enable docker to run on boot
sudo systemctl enable docker

# verify the test container
docker run hello-world

```

## Project Structure

```
job_board_platform/
├── docker/
│   ├── Dockerfile              # Multi-stage Dockerfile
│   ├── nginx/
│   │   ├── nginx.conf          # Development Nginx config
│   │   └── nginx.prod.conf     # Production Nginx config
│   ├── supervisor/
│   │   └── supervisord.conf    # Process management
│   ├── monitoring/
│   │   ├── prometheus.yml      # Metrics collection
│   │   └── grafana/           # Dashboard configs
│   └── logging/
│       └── fluentd.conf       # Log aggregation
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── .dockerignore              # Docker build exclusions
├── .env.example               # Environment variables template
└── scripts/
    └── docker_commands.sh     # Management scripts
```

## Quick Start

### 1. Initialize Project

```bash
# Make script executable
chmod +x scripts/docker_commands.sh

# Initialize project structure and create .env files
./scripts/docker_commands.sh init
```

### 2. Configure Environment

```bash
# Copy and customize environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

### 3. Start Development Environment

```bash
# Build and start all services
./scripts/docker_commands.sh dev-up


# Or manually:
docker-compose up -d --build
docker-compose build --no-cache

# migrate
docker-compose exec web python manage.py migrate
```

## 🔧 Development Environment

### Services Included

| Service | Port | Description |
|---------|------|-------------|
| **Django Web** | 8000 | Main application server |
| **PostgreSQL** | 5432 | Primary database |
| **Redis** | 6379 | Cache and message broker |
| **Elasticsearch** | 9200 | Search engine |
| **Celery Worker** | - | Background task processor |
| **Celery Beat** | - | Task scheduler |
| **Celery Flower** | 5555 | Task monitoring |
| **MailHog** | 8025 | Email testing |
| **MinIO** | 9001 | S3-compatible storage |

### Development Commands

```bash
# Start services
./scripts/docker_commands.sh dev-up

# View logs
./scripts/docker_commands.sh dev-logs web
./scripts/docker_commands.sh dev-logs

# Open shell in container
./scripts/docker_commands.sh dev-shell web
./scripts/docker_commands.sh dev-shell celery_worker

# Run tests
./scripts/docker_commands.sh dev-test

# Database operations
./scripts/docker_commands.sh dev-migrations    # Create migrations
./scripts/docker_commands.sh dev-migrate       # Apply migrations
./scripts/docker_commands.sh dev-backup        # Backup database
./scripts/docker_commands.sh dev-restore backup_file.sql

# Stop services
./scripts/docker_commands.sh dev-down
```

### Manual Docker Commands

```bash
# Build development image
docker-compose build

# Start services in background
docker-compose up -d

# View running containers
docker-compose ps

# Follow logs for all services
docker-compose logs -f

# Execute command in running container
docker-compose exec web python manage.py shell

# Stop all services
docker-compose down

# Remove volumes (⚠️ Data loss!)
docker-compose down -v
```

## 🏭 Production Environment

### Production Configuration

1. **Create production environment file:**
```bash
cp .env.prod.example .env.prod
```

2. **Configure production settings:**
```bash
# Edit production environment
nano .env.prod

# Required settings:
DEBUG=0
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=secure-production-password
```

3. **Deploy to production:**
```bash
./scripts/docker_commands.sh prod-deploy
```

### Production Services

| Service | Replicas | Description |
|---------|----------|-------------|
| **Nginx** | 1 | Load balancer & static files |
| **Django Web** | 3 | Application servers |
| **Celery Worker** | 2 | Background processors |
| **Celery Beat** | 1 | Task scheduler |
| **PostgreSQL** | 1 | Database with optimizations |
| **Redis** | 1 | Cache with persistence |
| **Elasticsearch** | 1 | Search with 2GB heap |
| **Prometheus** | 1 | Metrics collection |
| **Grafana** | 1 | Monitoring dashboards |

### Production Commands

```bash
# Build production images
./scripts/docker_commands.sh prod-build

# Deploy to production
./scripts/docker_commands.sh prod-deploy

# View production logs
./scripts/docker_commands.sh prod-logs nginx
./scripts/docker_commands.sh prod-logs web

# Backup production data
./scripts/docker_commands.sh prod-backup

# Stop production services
./scripts/docker_commands.sh prod-down
```

## 📊 Monitoring & Observability

### Access Points

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Application Health**: http://localhost/health/

### Health Checks

```bash
# Automated health check
./scripts/docker_commands.sh health

# Manual health checks
curl http://localhost:8000/health/      # Development
curl http://localhost/health/           # Production

# Check service status
./scripts/docker_commands.sh status
```

### Metrics Available

- **Application**: Request/response times, error rates, active users
- **Database**: Connection pools, query performance, disk usage
- **Cache**: Hit rates, memory usage, key statistics  
- **Search**: Index size, query performance, cluster health
- **System**: CPU, memory, disk, network utilization

## 🧪 Testing Environment

### Run Tests

```bash
# Run all tests
./scripts/docker_commands.sh dev-test

# Run specific test module
docker-compose exec web python manage.py test apps.jobs.tests

# Run tests with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
docker-compose exec web coverage html
```

### Test Database

```bash
# Create test database
docker-compose exec db createdb -U jobboard_user test_jobboard_dev

# Run tests against specific database
docker-compose exec web python manage.py test --settings=config.settings.testing
```

## 🔒 Security Considerations

### Production Security

1. **Environment Variables**
```bash
# Use secure secrets
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(50))')
DB_PASSWORD=$(openssl rand -base64 32)
```

2. **SSL/TLS Configuration**
```bash
# Generate SSL certificates (Let's Encrypt recommended)
mkdir -p docker/nginx/ssl
# Place your certificates in docker/nginx/ssl/
# Update nginx.prod.conf to enable HTTPS
```

3. **Database Security**
```bash
# Use strong passwords
# Enable SSL connections
# Regular security updates
```

4. **Container Security**
```bash
# Run as non-root user (already configured)
# Use minimal base images
# Regular image updates
# Scan for vulnerabilities
```

## 🔧 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill conflicting process
sudo kill -9 $(sudo lsof -t -i:8000)
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready -U jobboard_user

# Reset database
docker-compose down
docker volume rm $(docker volume ls -q | grep postgres)
docker-compose up -d db
```

#### Memory Issues
```bash
# Check container resource usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > 4GB+
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x scripts/docker_commands.sh

# Fix volume permissions
docker-compose exec web chown -R django:django /app/media
```

### Log Analysis

```bash
# Application logs
docker-compose logs web | grep ERROR

# Database logs
docker-compose logs db | tail -100

# All service logs with timestamps
docker-compose logs -t -f

# Filter logs by service
docker-compose logs celery_worker | grep -i "task"
```

### Performance Optimization

#### Database Performance
```bash
# Monitor slow queries
docker-compose exec db psql -U jobboard_user -d jobboard_dev -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

#### Redis Performance
```bash
# Monitor Redis memory usage
docker-compose exec redis redis-cli info memory

# Check slow queries
docker-compose exec redis redis-cli slowlog get 10
```

#### Application Performance
```bash
# Monitor Django debug toolbar (development)
# Add 'debug_toolbar' to INSTALLED_APPS

# Profile with django-extensions
docker-compose exec web python manage.py runprofileserver
```

## 📦 Backup & Recovery

### Automated Backups

```bash
# Development backup
./scripts/docker_commands.sh dev-backup

# Production backup (includes database + media)
./scripts/docker_commands.sh prod-backup

# Schedule daily backups (add to crontab)
0 2 * * * /path/to/job_board_platform/scripts/docker_commands.sh prod-backup
```

### Manual Backup Procedures

```bash
# Database backup
docker-compose exec db pg_dump -U jobboard_user jobboard_dev > backup_$(date +%Y%m%d).sql

# Media files backup
docker cp $(docker-compose ps -q web):/app/media ./media_backup_$(date +%Y%m%d)

# Full system backup
tar -czf full_backup_$(date +%Y%m%d).tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='node_modules' \
  .
```

### Disaster Recovery

```bash
# Restore database
docker-compose exec -T db psql -U jobboard_user -d jobboard_dev < backup.sql

# Restore media files
docker cp ./media_backup $(docker-compose ps -q web):/app/media

# Restore full system
tar -xzf full_backup.tar.gz
./scripts/docker_commands.sh dev-up
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/docker.yml
name: Docker Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build development image
      run: docker-compose build
    
    - name: Run tests
      run: |
        docker-compose up -d db redis
        docker-compose run web python manage.py test
        
    - name: Clean up
      run: docker-compose down -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Add your deployment script here
        ./scripts/docker_commands.sh prod-deploy
```

## 📚 Additional Resources

### Useful Docker Commands

```bash
# System cleanup
docker system prune -a              # Remove all unused containers, images
docker volume prune                 # Remove all unused volumes
docker network prune               # Remove all unused networks

# Image management
docker images                      # List all images
docker rmi $(docker images -q)    # Remove all images
docker pull postgres:15-alpine    # Update base image

# Container debugging
docker inspect container_name      # Detailed container info
docker exec -it container_name bash  # Interactive shell
docker logs --tail 50 container_name # Recent logs
```

### Environment Variables Reference

```bash
# Django Settings
DEBUG=0/1                         # Debug mode
SECRET_KEY=string                 # Django secret key
ALLOWED_HOSTS=comma,separated     # Allowed host names
DJANGO_SETTINGS_MODULE=config.settings.production

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
DB_NAME=database_name
DB_USER=database_user
DB_PASSWORD=database_password
DB_HOST=database_host
DB_PORT=5432

# Cache & Message Broker
REDIS_URL=redis://host:port/db
CELERY_BROKER_URL=redis://host:port/db
CELERY_RESULT_BACKEND=redis://host:port/db

# Search
ELASTICSEARCH_URL=http://host:port
ELASTICSEARCH_INDEX_PREFIX=jobboard

# Storage
AWS_ACCESS_KEY_ID=key
AWS_SECRET_ACCESS_KEY=secret
AWS_STORAGE_BUCKET_NAME=bucket
AWS_S3_REGION_NAME=us-east-1
USE_S3=True/False

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=password
EMAIL_USE_TLS=True/False
EMAIL_USE_SSL=True/False

# Monitoring
SENTRY_DSN=https://key@sentry.io/project
```

### Performance Tuning Tips

1. **Database Optimization**
   - Use connection pooling
   - Optimize queries with indexes
   - Regular VACUUM and ANALYZE
   - Monitor slow query log

2. **Caching Strategy**
   - Redis for session storage
   - Database query caching
   - Template fragment caching
   - Static file caching with CDN

3. **Application Scaling**
   - Use multiple Gunicorn workers
   - Implement horizontal pod autoscaling
   - Load balance with Nginx
   - Monitor response times

4. **Resource Management**
   - Set container memory limits
   - Use multi-stage builds
   - Optimize Docker layer caching
   - Regular image updates

### Monitoring Setup

1. **Application Metrics**
```python
# Add to requirements/production.txt
django-prometheus==2.2.0
prometheus-client==0.16.0

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

# Add to middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

2. **Custom Metrics**
```python
from prometheus_client import Counter, Histogram, Gauge

# Custom metrics
job_applications = Counter('job_applications_total', 'Total job applications')
job_search_duration = Histogram('job_search_duration_seconds', 'Job search duration')
active_jobs = Gauge('active_jobs_count', 'Number of active job postings')
```

### Support

For issues and questions:
- Check the troubleshooting section above
- Review Docker and Django logs
- Create an issue in the project repository
- Consult Docker and Django documentation

## 📝 Changelog

### v1.0.0 (Initial Release)
- Multi-stage Dockerfile with development/production targets
- Docker Compose configurations for all environments
- Comprehensive monitoring with Prometheus and Grafana
- Automated backup and recovery scripts
- Security hardening and best practices
- Complete documentation and troubleshooting guide

## Common Errors

## check if a process is using a port
```bash
sudo netstat -tulpn | grep :5432
or 
# Windows and Mac
sudo lsof -i :5432

# stop local {postgres} if installed
sudo systemctl stop postgresql  # Ubuntu/Debian
sudo service postgresql stop    # Alternative
brew services stop postgresql   # macOS with Homebrew

# kill the process if not postgres
sudo kill -9 <PID>  # Replace <PID> with the process ID from netstat/lsof

# Option B: Stop or Remove Conflicting Docker ContainerIf another Docker container is using port 5432:List Running Containers:bash

docker ps

Look for a container using port 5432 (e.g., another PostgreSQL container).
Stop the Conflicting Container:bash

docker stop <container_id>

Remove It (if not needed):bash

docker rm <container_id>

Check for Orphaned Containers:bash

docker ps -a | grep 5432

Remove any stopped containers:bash

docker rm $(docker ps -a -q)

# Step-by-Step Resolution1. Identify the Process Using Port 6379Determine what’s occupying port 6379 on your host machine:bash

sudo netstat -tulpn | grep :6379

Or, on macOS/Windows:bash

sudo lsof -i :6379

Possible Outputs:Local Redis: You might see redis-server running, indicating a locally installed Redis instance.
Another Container: A Docker container ID might appear, indicating a conflicting container.
Other Application: A different process (less common).

2. Resolve the Port ConflictChoose one of these solutions based on what’s using the port:Option A: Stop the Conflicting ProcessIf a local Redis server or another application is using port 6379:Stop Local Redis (if installed):bash

sudo systemctl stop redis       # Ubuntu/Debian
sudo service redis stop         # Alternative
brew services stop redis        # macOS with Homebrew

Kill Other Process (if not Redis):bash

sudo kill -9 <PID>  # Replace <PID> with the process ID from netstat/lsof

Verify the port is free:bash

sudo netstat -tulpn | grep :6379

If no output, the port is free.

Option B: Stop or Remove Conflicting Docker ContainerIf another Docker container is using port 6379:List Running Containers:bash

docker ps

Look for a container exposing port 6379 (e.g., another Redis container).
Stop the Conflicting Container:bash

docker stop <container_id>

Remove It (if not needed):bash

docker rm <container_id>

Check for Orphaned Containers:bash

docker ps -a | grep 6379

Remove any stopped containers:bash

docker rm $(docker ps -a -q)

Step-by-Step Resolution1. Identify the Process Using Port 6379Determine what’s occupying port 6379 on your host machine:bash

sudo netstat -tulpn | grep :6379

Or, on macOS/Windows:bash

sudo lsof -i :6379

Possible Outputs:Local Redis: You might see redis-server running, indicating a locally installed Redis instance.
Another Container: A Docker container ID might appear, indicating a conflicting container.
Other Application: A different process (less common).

2. Resolve the Port ConflictChoose one of these solutions based on what’s using the port:Option A: Stop the Conflicting ProcessIf a local Redis server or another application is using port 6379:Stop Local Redis (if installed):bash

sudo systemctl stop redis       # Ubuntu/Debian
sudo service redis stop         # Alternative
brew services stop redis        # macOS with Homebrew

Kill Other Process (if not Redis):bash

sudo kill -9 <PID>  # Replace <PID> with the process ID from netstat/lsof

Verify the port is free:bash

sudo netstat -tulpn | grep :6379

If no output, the port is free.

Option B: Stop or Remove Conflicting Docker ContainerIf another Docker container is using port 6379:List Running Containers:bash

docker ps

Look for a container exposing port 6379 (e.g., another Redis container).
Stop the Conflicting Container:bash

docker stop <container_id>

Remove It (if not needed):bash

docker rm <container_id>

Check for Orphaned Containers:bash

docker ps -a | grep 6379

Remove any stopped containers:bash

docker rm $(docker ps -a -q)

# Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint jobboard_redis (d81e786741faa0bc0caedfed4a967b283c3f97a3d33c2b8979b313a24d0d59f5): failed to bind host port for 0.0.0.0:6379:172.20.0.5:6379/tcp: address already in use

Step-by-Step Resolution1. Identify the Process Using Port 6379Determine what’s occupying port 6379 on your host machine:bash

sudo netstat -tulpn | grep :6379

Or, on macOS/Windows:bash

sudo lsof -i :6379

Possible Outputs:Local Redis: You might see redis-server running, indicating a locally installed Redis instance.
Another Container: A Docker container ID might appear, indicating a conflicting container.
Other Application: A different process (less common).

2. Resolve the Port ConflictChoose one of these solutions based on what’s using the port:Option A: Stop the Conflicting ProcessIf a local Redis server or another application is using port 6379:Stop Local Redis (if installed):bash

sudo systemctl stop redis       # Ubuntu/Debian
sudo service redis stop         # Alternative
brew services stop redis        # macOS with Homebrew

Kill Other Process (if not Redis):bash

sudo kill -9 <PID>  # Replace <PID> with the process ID from netstat/lsof

Verify the port is free:bash

sudo netstat -tulpn | grep :6379

If no output, the port is free.

Option B: Stop or Remove Conflicting Docker ContainerIf another Docker container is using port 6379:List Running Containers:bash

docker ps

Look for a container exposing port 6379 (e.g., another Redis container).
Stop the Conflicting Container:bash

docker stop <container_id>

Remove It (if not needed):bash

docker rm <container_id>

Check for Orphaned Containers:bash

docker ps -a | grep 6379

Remove any stopped containers:bash

docker rm $(docker ps -a -q)

# Stop all containers and clean up
docker-compose down -v
docker system prune -f

# to see all urls
docker-compose logs urls
# or view all logs
docker-compose logs -f

# for database conflicts, find and remove any existing migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && find . -path "*/migrations/*.pyc" -delete

# show migrations
docker-compose exec web python manage.py showmigrations

# create and apply migrations
docker-compose exec web python manage.py makemigrations {app name}

# migrate
docker-compose exec web python manage.py migrate accounts {app name}