#!/bin/sh
set -e
echo "Starting database migrations..."
alembic upgrade head
echo "Database migrations completed. Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
