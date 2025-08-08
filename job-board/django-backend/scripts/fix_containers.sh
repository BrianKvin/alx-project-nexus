#!/bin/bash

echo "=== Stopping and cleaning up containers ==="
docker-compose down -v
docker system prune -f --volumes

echo -e "\n=== Creating necessary directories ==="
mkdir -p scripts
mkdir -p config/settings
mkdir -p static
mkdir -p media
mkdir -p templates

echo -e "\n=== Creating init_db.sql script ==="
cat > scripts/init_db.sql << 'EOF'
-- Initialize job board database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
SELECT 'Job Board Database initialized successfully!' as message;
EOF

echo -e "\n=== Setting proper permissions ==="
chmod +x scripts/init_db.sql

echo -e "\n=== Checking port availability ==="
netstat -tulpn | grep :5432 && echo "Port 5432 is in use!" || echo "Port 5432 is available"
netstat -tulpn | grep :6379 && echo "Port 6379 is in use!" || echo "Port 6379 is available"
netstat -tulpn | grep :9200 && echo "Port 9200 is in use!" || echo "Port 9200 is available"

echo -e "\n=== Starting services one by one ==="

echo "Starting database..."
docker-compose up -d db
sleep 10

echo "Checking database logs..."
docker logs jobboard_db

echo "Testing database connection..."
timeout 30 bash -c 'until docker exec jobboard_db pg_isready -U jobboard_user -d jobboard_dev; do sleep 2; done' && echo "Database is ready!" || echo "Database failed to start"

if [ $? -eq 0 ]; then
    echo "Starting Redis..."
    docker-compose up -d redis
    sleep 5
    
    echo "Starting Elasticsearch..."
    docker-compose up -d elasticsearch
    sleep 15
    
    echo "Starting remaining services..."
    docker-compose up -d
else
    echo "Database failed to start. Check the logs above."
    exit 1
fi

echo -e "\n=== Final Status Check ==="
docker-compose ps