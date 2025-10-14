#!/bin/bash

# Create data directories if they don't exist
mkdir -p /app/data/index
mkdir -p /app/data/uploads  
mkdir -p /app/data/ingested

# Set proper permissions
chmod -R 755 /app/data/

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
