#!/bin/bash

echo "=== COMPLETE DOCKER RESET ==="
echo "This will remove all containers, volumes, and data. Continue? (y/n)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo -e "\n=== Stopping all containers ==="
docker-compose down -v

echo -e "\n=== Removing all jobboard-related containers ==="
docker rm -f $(docker ps -aq --filter "name=jobboard") 2>/dev/null || echo "No jobboard containers to remove"

echo -e "\n=== Removing all jobboard-related volumes ==="
docker volume rm $(docker volume ls -q | grep django-backend) 2>/dev/null || echo "No volumes to remove"

echo -e "\n=== Removing all jobboard-related networks ==="
docker network rm $(docker network ls -q --filter "name=jobboard") 2>/dev/null || echo "No networks to remove"

echo -e "\n=== Cleaning Docker system ==="
docker system prune -f

echo -e "\n=== Checking for local PostgreSQL conflicts ==="
sudo netstat -tulpn | grep :5432 && echo "WARNING: Something is using port 5432!" || echo "Port 5432 is free"
sudo netstat -tulpn | grep :6379 && echo "WARNING: Something is using port 6379!" || echo "Port 6379 is free"
sudo netstat -tulpn | grep :9200 && echo "WARNING: Something is using port 9200!" || echo "Port 9200 is free"

echo -e "\n=== Creating fresh directories ==="
mkdir -p scripts config/settings static media templates

echo -e "\n=== Starting fresh containers ==="
echo "Starting database..."
docker-compose up -d db

echo "Waiting 15 seconds for database initialization..."
sleep 15

docker logs jobboard_db

echo -e "\n=== Testing database ==="
if docker exec jobboard_db pg_isready -U jobboard_user -d jobboard_dev >/dev/null 2>&1; then
    echo "✓ Database is working!"
    
    echo "Starting remaining services..."
    docker-compose up -d
    
    echo -e "\n=== Final status ==="
    docker-compose ps
    
    echo -e "\n=== Service URLs ==="
    echo "Django: http://localhost:8000"
    echo "MailHog: http://localhost:8025"
    echo "MinIO: http://localhost:9001"
    echo "Flower: http://localhost:5555"
    echo "Elasticsearch: http://localhost:9200"
    
else
    echo "✗ Database failed to start!"
    echo "Database logs:"
    docker logs jobboard_db
fi