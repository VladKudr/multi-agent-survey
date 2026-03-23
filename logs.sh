#!/bin/bash

# View logs for Multi-Agent Survey Simulation Platform

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

if [ -z "$1" ]; then
    echo "📋 Viewing all logs (Ctrl+C to exit)..."
    $COMPOSE_CMD logs -f
else
    echo "📋 Viewing logs for: $1"
    $COMPOSE_CMD logs -f "$1"
fi
