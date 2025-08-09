#!/bin/bash
# scripts/docker_env_manager.sh - Docker environment manager for Job Board Platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
}

# Development environment commands
dev_build() {
    print_status "Building development environment..."
    check_docker
    check_compose
    
    docker-compose -f docker-compose.yml build --no-cache
    print_success "Development build completed"
}

dev_up() {
    print_status "Starting development environment..."
    check_docker
    check_compose
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_warning ".env file not found, copying from .env.example"
        cp .env.example .env
    fi
    
    # Build and start containers
    print_status "Building and starting containers..."
    docker-compose -f docker-compose.yml up -d --build
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    until docker-compose -f docker-compose.yml exec db pg_isready -U jobboard_user -d jobboard_dev >/dev/null 2>&1; do
        sleep 2
        echo -n "."
    done
    echo ""
    
    # Run migrations with memory optimizations
    print_status "Running database migrations..."
    if ! docker-compose -f docker-compose.yml exec -T web python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
import django
django.setup()
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    "; then
        print_error "Failed to run migrations. Retrying with more memory..."
        # Try again with increased memory limit
        if ! docker-compose -f docker-compose.yml run --rm --entrypoint="" web \
            sh -c "python manage.py migrate --noinput"; then
            print_error "Failed to run migrations after retry. Check the logs with: docker-compose logs web"
            exit 1
        fi
    fi
    
    # Create or reset admin user
    print_status "Setting up admin user..."
    if ! docker-compose -f docker-compose.yml exec -T web python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

try:
    # Try to get the admin user
    admin = User.objects.get(email='admin@jobboard.com')
    print('Admin user exists. Resetting password...')
    admin.set_password('admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
    print('Admin password has been reset.')
except User.DoesNotExist:
    print('Creating admin user...')
    User.objects.create_superuser(email='admin@jobboard.com', password='admin')
    print('Admin user created successfully')
" 2>/dev/null; then
        print_warning "Could not set up admin user"
    fi
    
    # Load fixtures if available
    if [ -d "fixtures" ]; then
        print_status "Loading fixtures..."
        docker-compose -f docker-compose.yml exec web python manage.py loaddata fixtures/*.json
    fi
    
    print_success "Development environment is running!"
    print_status "Services available at:"
    echo "  - Django Admin: http://localhost:8000/admin"
    echo "  - API Documentation (Swagger UI): http://localhost:8000/swagger/"
    echo "  - API Documentation (ReDoc): http://localhost:8000/redoc/"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - Elasticsearch: http://localhost:9200"
    echo "  - Celery Flower: http://localhost:5555"
    echo "  - MailHog: http://localhost:8025"
    echo "  - MinIO: http://localhost:9001"
}

dev_down() {
    print_status "Stopping development environment..."
    docker-compose -f docker-compose.yml down
    print_success "Development environment stopped"
}

dev_restart() {
    print_status "Restarting development environment..."
    dev_down
    dev_up
}

dev_logs() {
    service=${1:-""}
    if [ -n "$service" ]; then
        docker-compose -f docker-compose.yml logs -f "$service"
    else
        docker-compose -f docker-compose.yml logs -f
    fi
}

dev_shell() {
    service=${1:-web}
    print_status "Opening shell in $service container..."
    docker-compose -f docker-compose.yml exec "$service" /bin/bash
}

dev_test() {
    print_status "Running tests in development environment..."
    docker-compose -f docker-compose.yml exec web python manage.py test --verbosity=2
}

dev_makemigrations() {
    print_status "Creating database migrations..."
    docker-compose -f docker-compose.yml exec web python manage.py makemigrations
}

dev_migrate() {
    print_status "Applying database migrations..."
    docker-compose -f docker-compose.yml exec web python manage.py migrate
}

dev_collectstatic() {
    print_status "Collecting static files..."
    docker-compose -f docker-compose.yml exec web python manage.py collectstatic --noinput
}

dev_backup_db() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backup_${timestamp}.sql"
    
    print_status "Creating database backup: $backup_file"
    docker-compose -f docker-compose.yml exec db pg_dump -U jobboard_user jobboard_dev > "backups/$backup_file"
    print_success "Database backup created: backups/$backup_file"
}

dev_restore_db() {
    backup_file=$1
    if [ -z "$backup_file" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi
    
    print_warning "This will restore the database. All current data will be lost!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restoring database from: $backup_file"
        docker-compose -f docker-compose.yml exec -T db psql -U jobboard_user -d jobboard_dev < "$backup_file"
        print_success "Database restored successfully"
    else
        print_status "Database restore cancelled"
    fi
}

# Production environment commands
prod_build() {
    print_status "Building production environment..."
    check_docker
    check_compose
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    print_success "Production build completed"
}

prod_deploy() {
    print_status "Deploying to production..."
    check_docker
    check_compose
    
    # Check if .env.prod exists
    if [ ! -f .env.prod ]; then
        print_error ".env.prod file not found. Please create it with production settings."
        exit 1
    fi
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
    
    # Wait for services
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run migrations
    print_status "Running production migrations..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --noinput
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --noinput
    
    print_success "Production deployment completed!"
    print_status "Services available at:"
    echo "  - Application: http://localhost (port 80)"
    echo "  - Monitoring: http://localhost:9090 (Prometheus)"
    echo "  - Dashboard: http://localhost:3000 (Grafana)"
}

prod_down() {
    print_status "Stopping production environment..."
    docker-compose -f docker-compose.prod.yml down
    print_success "Production environment stopped"
}

prod_logs() {
    service=${1:-""}
    if [ -n "$service" ]; then
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    else
        docker-compose -f docker-compose.prod.yml logs -f
    fi
}

prod_backup() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/prod_${timestamp}"
    mkdir -p "$backup_dir"
    
    print_status "Creating production backup: $backup_dir"
    
    # Database backup
    docker-compose -f docker-compose.prod.yml exec db pg_dump -U "$DB_USER" "$DB_NAME" > "$backup_dir/database.sql"
    
    # Media files backup
    docker cp $(docker-compose -f docker-compose.prod.yml ps -q web):/app/media "$backup_dir/"
    
    # Configuration backup
    cp .env.prod "$backup_dir/"
    cp docker-compose.prod.yml "$backup_dir/"
    
    print_success "Production backup created: $backup_dir"
}

# Utility functions
clean_containers() {
    print_status "Cleaning up stopped containers..."
    docker container prune -f
    print_success "Containers cleaned"
}

clean_images() {
    print_status "Cleaning up unused images..."
    docker image prune -af
    print_success "Images cleaned"
}

clean_volumes() {
    print_warning "This will remove all unused volumes. Data may be lost!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up unused volumes..."
        docker volume prune -f
        print_success "Volumes cleaned"
    else
        print_status "Volume cleanup cancelled"
    fi
}

clean_all() {
    clean_containers
    clean_images
    clean_volumes
}

show_status() {
    print_status "Docker system information:"
    docker system df
    echo
    
    print_status "Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    
    print_status "Docker compose services (development):"
    docker-compose -f docker-compose.yml ps 2>/dev/null || echo "Development environment not running"
    echo
    
    print_status "Docker compose services (production):"
    docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "Production environment not running"
}

init_project() {
    print_status "Initializing project structure..."
    
    # Create necessary directories
    mkdir -p {backups,logs/{django,nginx,celery},docker/{nginx,monitoring,logging}}
    mkdir -p scripts
    
    # Create .env.example if it doesn't exist
    if [ ! -f .env.example ]; then
        cat > .env.example << 'EOF'
# Development Environment Variables
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=jobboard_dev
DB_USER=jobboard_user
DB_PASSWORD=dev_password_123
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# Email (MailHog for development)
EMAIL_HOST=mailhog
EMAIL_PORT=1025
EMAIL_USE_TLS=0

# AWS S3 (for production)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Monitoring
GRAFANA_PASSWORD=admin
EOF
    fi
    
    # Create production env template
    if [ ! -f .env.prod.example ]; then
        cat > .env.prod.example << 'EOF'
# Production Environment Variables
DEBUG=0
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=jobboard_prod
DB_USER=jobboard_user
DB_PASSWORD=secure_production_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# Email
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=1

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket

# Monitoring
GRAFANA_PASSWORD=secure_grafana_password
EOF
    fi
    
    print_success "Project initialized successfully!"
}

# Health check function
health_check() {
    print_status "Performing health checks..."
    
    # Check if development environment is running
    if docker-compose -f docker-compose.yml ps | grep -q "Up"; then
        print_status "Development environment status:"
        
        # Check web service
        if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
            print_success "Web service: OK"
        else
            print_error "Web service: FAILED"
        fi
        
        # Check database
        if docker-compose -f docker-compose.yml exec db pg_isready -U jobboard_user >/dev/null 2>&1; then
            print_success "Database: OK"
        else
            print_error "Database: FAILED"
        fi
        
        # Check Redis
        if docker-compose -f docker-compose.yml exec redis redis-cli ping >/dev/null 2>&1; then
            print_success "Redis: OK"
        else
            print_error "Redis: FAILED"
        fi
        
        # Check Elasticsearch
        if curl -f http://localhost:9200/_cluster/health >/dev/null 2>&1; then
            print_success "Elasticsearch: OK"
        else
            print_error "Elasticsearch: FAILED"
        fi
    else
        print_warning "Development environment is not running"
    fi
}

# Help function
show_help() {
    echo "Job Board Platform - Docker Management Script"
    echo "============================================="
    echo
    echo "Development Commands:"
    echo "  dev-build       - Build development environment"
    echo "  dev-up          - Start development environment"
    echo "  dev-down        - Stop development environment"
    echo "  dev-restart     - Restart development environment"
    echo "  dev-logs [svc]  - Show logs (optional service name)"
    echo "  dev-shell [svc] - Open shell in container (default: web)"
    echo "  dev-test        - Run tests"
    echo "  dev-migrations  - Create database migrations"
    echo "  dev-migrate     - Apply database migrations"
    echo "  dev-static      - Collect static files"
    echo "  dev-backup      - Backup development database"
    echo "  dev-restore     - Restore development database"
    echo
    echo "Production Commands:"
    echo "  prod-build      - Build production environment"
    echo "  prod-deploy     - Deploy to production"
    echo "  prod-down       - Stop production environment"
    echo "  prod-logs [svc] - Show production logs"
    echo "  prod-backup     - Backup production data"
    echo
    echo "Utility Commands:"
    echo "  clean-containers - Remove stopped containers"
    echo "  clean-images    - Remove unused images"
    echo "  clean-volumes   - Remove unused volumes"
    echo "  clean-all       - Clean containers, images, and volumes"
    echo "  status          - Show system status"
    echo "  health          - Perform health checks"
    echo "  init            - Initialize project structure"
    echo "  help            - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 dev-up                    # Start development environment"
    echo "  $0 dev-logs web             # Show web container logs"
    echo "  $0 dev-shell celery_worker  # Open shell in celery worker"
    echo "  $0 prod-deploy              # Deploy to production"
}

# Main script logic
case "$1" in
    dev-build)      dev_build ;;
    dev-up)         dev_up ;;
    dev-down)       dev_down ;;
    dev-restart)    dev_restart ;;
    dev-logs)       dev_logs "$2" ;;
    dev-shell)      dev_shell "$2" ;;
    dev-test)       dev_test ;;
    dev-migrations) dev_makemigrations ;;
    dev-migrate)    dev_migrate ;;
    dev-static)     dev_collectstatic ;;
    dev-backup)     dev_backup_db ;;
    dev-restore)    dev_restore_db "$2" ;;
    prod-build)     prod_build ;;
    prod-deploy)    prod_deploy ;;
    prod-down)      prod_down ;;
    prod-logs)      prod_logs "$2" ;;
    prod-backup)    prod_backup ;;
    clean-containers) clean_containers ;;
    clean-images)   clean_images ;;
    clean-volumes)  clean_volumes ;;
    clean-all)      clean_all ;;
    status)         show_status ;;
    health)         health_check ;;
    init)           init_project ;;
    help|--help|-h) show_help ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac