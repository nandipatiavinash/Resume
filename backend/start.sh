#!/bin/sh
set -e
echo "Starting database migrations..."
alembic upgrade head
echo "Database migrations completed."

echo "Starting Celery worker in the background..."
celery -A app.tasks.celery_app.celery_app worker --loglevel=info --concurrency=1 &

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
