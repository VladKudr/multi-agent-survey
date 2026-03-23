#!/bin/bash

# Start script for Multi-Agent Survey Simulation Platform
# This script starts all required services

set -e

echo "🚀 Starting Multi-Agent Survey Simulation Platform..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for docker compose (v2) or docker-compose (v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Using: $COMPOSE_CMD"

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your SECRET_KEY if needed"
fi

# Build and start services
echo "🔨 Building and starting services..."
cd infra
$COMPOSE_CMD up -d --build

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔌 API:      http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "   cd infra && $COMPOSE_CMD logs -f"
echo ""
echo "To stop:"
echo "   cd infra && $COMPOSE_CMD down"
echo ""
