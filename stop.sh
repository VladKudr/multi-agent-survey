#!/bin/bash

# Stop script for Multi-Agent Survey Simulation Platform

set -e

echo "🛑 Stopping Multi-Agent Survey Simulation Platform..."

# Check for docker compose (v2) or docker-compose (v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose is not installed"
    exit 1
fi

cd infra
$COMPOSE_CMD down

echo "✅ Services stopped!"
