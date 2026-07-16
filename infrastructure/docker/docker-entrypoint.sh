#!/bin/sh
# Docker Entrypoint — lumay-si-ai-hub
set -e

# Run database migrations
if [ "$APP_ENV" != "production" ] || [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Execute the main command
exec "$@"
