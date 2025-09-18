#!/usr/bin/env bash

# Django Backend Server Startup Script
echo "Starting Django Backend Server..."

# Navigate to the backend directory
cd "$(dirname "$0")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing/updating dependencies..."
    python3 -m pip install -r requirements.txt
fi

# Run migrations
echo "Running database migrations..."
python3 manage.py migrate

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Start the development server
echo "Starting Django development server at http://127.0.0.1:8000/"
echo "Press CTRL+C to stop the server"
python3 manage.py runserver