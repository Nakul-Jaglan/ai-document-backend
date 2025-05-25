#!/bin/bash

# Load environment variables from .env file
if [ -f ../.env ]; then
    export $(cat ../.env | xargs)
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY is not set in .env file"
    exit 1
fi

# Make the environment variables available to Django
python ../manage.py shell << END
import os
os.environ["GEMINI_API_KEY"] = "$GEMINI_API_KEY"
END

echo "Environment variables set successfully!"
