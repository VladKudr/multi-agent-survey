#!/bin/bash

# Check status of Multi-Agent Survey Simulation Platform services

# Check for docker compose (v2) or docker-compose (v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "📊 Service Status:"
echo ""
cd infra
$COMPOSE_CMD ps

echo ""
echo "🔍 Health Check:"
echo ""

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend: http://localhost:8000 - OK"
else
    echo "❌ Backend: http://localhost:8000 - Not responding"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:3000 - OK"
else
    echo "❌ Frontend: http://localhost:3000 - Not responding"
fi

echo ""
echo "📱 Quick Links:"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:8000"
echo "   Docs:     http://localhost:8000/docs"
