#!/bin/bash
# ─── Docker Entrypoint Script ─────────────────────────────────
# Runs database migrations, collects static files,
# then starts the application server.

set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Ensuring super_admin exists..."
python manage.py promote_admin

echo "==> Creating log directory..."
mkdir -p /app/logs

echo "==> Starting application..."
exec "$@"
