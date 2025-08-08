#!/bin/bash

echo "=== Database Container Logs ==="
docker logs jobboard_db

echo -e "\n=== Database Container Status ==="
docker inspect jobboard_db --format='{{.State.Status}}: {{.State.Error}}'

echo -e "\n=== Database Container Exit Code ==="
docker inspect jobboard_db --format='{{.State.ExitCode}}'

echo -e "\n=== Checking PostgreSQL Data Volume ==="
docker volume inspect django-backend_postgres_data

echo -e "\n=== Checking if init script exists ==="
ls -la ./scripts/init_db.sql 2>/dev/null || echo "init_db.sql not found"

echo -e "\n=== Checking PostgreSQL permissions ==="
docker run --rm -v django-backend_postgres_data:/data alpine ls -la /data || echo "Volume inspection failed"