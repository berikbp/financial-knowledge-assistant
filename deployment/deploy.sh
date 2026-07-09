#!/usr/bin/env bash

set -e

echo "Checking required files..."

if [ ! -f ".env.production" ]; then
  echo "ERROR: .env.production not found."
  exit 1
fi

if [ ! -f "cache/chunks.json" ]; then
  echo "ERROR: cache/chunks.json not found."
  echo "Run: uv run python -m cache.build_chunk"
  exit 1
fi

if [ ! -d "qdrant_storage" ]; then
  echo "WARNING: qdrant_storage folder not found."
  echo "If Qdrant index is missing, run indexing before deployment."
fi

echo "Starting production Docker Compose stack..."

docker compose -f docker-compose.prod.yml up --build -d

echo "Containers:"
docker compose -f docker-compose.prod.yml ps

echo "Deployment started."
echo "API health: http://YOUR_EC2_PUBLIC_IP:8000/health"
echo "Frontend:   http://YOUR_EC2_PUBLIC_IP:5500"
