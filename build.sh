#!/usr/bin/env bash

# Exit on error
set -o errexit

# Create a .env file with necessary environment variables
echo "DJANGO_SETTINGS_MODULE=tutorflow.settings" > .env
echo "DEBUG=False" >> .env
echo "OPENAI_API_KEY=${OPENAI_API_KEY:-}" >> .env
echo "GEMINI_API_KEY=${GEMINI_API_KEY:-}" >> .env
echo "DJANGO_SECRET_KEY=${SECRET_KEY:-}" >> .env

# Display Python version
python --version

# Install python dependencies
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

echo "Build completed successfully!"
