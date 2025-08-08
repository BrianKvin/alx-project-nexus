# Multi-stage Dockerfile for Django Job Board Platform

# Stage 1: Base Python image with system dependencies
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    # Database clients
    postgresql-client \
    libpq-dev \
    # Media processing
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    # Other utilities
    curl \
    wget \
    git \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django

# Stage 2: Development dependencies
FROM base AS development

# Install development system dependencies
RUN apt-get update && apt-get install -y \
    # Development tools
    vim \
    less \
    tree \
    # Debugging tools
    strace \
    tcpdump \
    netcat-openbsd \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements/base.txt requirements/development.txt requirements/
RUN pip install --no-cache-dir -r requirements/development.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs

# Set proper permissions
RUN chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Development command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Stage 3: Production base
FROM base AS production-base

# Install production system dependencies
RUN apt-get update && apt-get install -y \
    # Web server
    # nginx \ - not strictly required with gunicorn in place
    # Process manager
    # supervisor \ - not strictly required with gunicorn in place
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements/base.txt requirements/production.txt requirements/
RUN pip install --no-cache-dir -r requirements/production.txt \
    && pip install gunicorn

# Stage 4: Production
FROM production-base AS production

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs /var/log/supervisor

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Set proper permissions
RUN chown -R django:django /app /var/log/supervisor

# Copy configuration files
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose ports
EXPOSE 80 8000

# Switch to non-root user
USER django

# Production command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Stage 5: Testing
FROM development AS testing

# Install testing dependencies
COPY requirements/testing.txt requirements/
RUN pip install --no-cache-dir -r requirements/testing.txt

# Set testing environment
ENV DJANGO_SETTINGS_MODULE=config.settings.testing

# Command for running tests
CMD ["python", "manage.py", "test", "--verbosity=2"]