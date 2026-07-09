#!/usr/bin/env bash

set -e

echo "Stopping production Docker Compose stack..."

docker compose -f docker-compose.prod.yml down

echo "Stopped."
