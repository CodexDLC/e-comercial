#!/bin/sh
set -e

# If a command is passed (e.g. migrate), run only that
if [ "$#" -gt 0 ]; then
    echo "Running command: $@"
    exec "$@"
fi

echo "Running collectstatic..."
# Health and path check
echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Checking environment..."
echo "PYTHONPATH: $PYTHONPATH"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Create logs directory if it doesn't exist (though it should be a volume)
mkdir -p /app/logs

if [ "$ENVIRONMENT" != "testing" ]; then
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Collecting static files..."
    python /app/manage.py collectstatic --noinput

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Running migrations..."
    python /app/manage.py migrate --noinput

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Updating content..."
    python /app/manage.py update_all_content
else
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Environment: testing | Skipping collectstatic, migrations and content updates for speed."
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] (Tests use SQLite in-memory, Docker DB is only verified for connectivity)"
fi

echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Starting gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout 90 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log \
    --capture-output \
    --log-level info
