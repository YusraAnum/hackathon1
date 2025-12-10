#!/bin/bash
# Production startup script for AI-Native Textbook backend

set -e  # Exit on any error

echo "Starting AI-Native Textbook backend in production mode..."

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    exit 1
fi

if [ -z "$NEON_DB_URL" ]; then
    echo "Error: NEON_DB_URL environment variable is not set"
    exit 1
fi

if [ -z "$QDRANT_URL" ]; then
    echo "Error: QDRANT_URL environment variable is not set"
    exit 1
fi

# Set production environment variables
export ENVIRONMENT=production
export DEBUG=False

# Run pre-startup checks
echo "Running pre-startup checks..."
python -c "
import os
import sys

# Check if required modules are available
try:
    import fastapi
    import uvicorn
    import pydantic_settings
    import psycopg2
    import qdrant_client
    print('✓ All required modules are available')
except ImportError as e:
    print(f'✗ Missing required module: {e}')
    sys.exit(1)

# Check if environment variables are properly set
required_vars = ['OPENAI_API_KEY', 'NEON_DB_URL', 'QDRANT_URL']
for var in required_vars:
    if not os.getenv(var):
        print(f'✗ Required environment variable {var} is not set')
        sys.exit(1)
print('✓ All required environment variables are set')
"

# Start the application with uvicorn
echo "Starting application server..."
exec uvicorn main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --timeout-keep-alive 30 \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --forwarded-allow-ips "*"