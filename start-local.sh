#!/bin/bash

# Local development startup (without Docker)
# Requires: Python 3.11+, Node.js 20+, PostgreSQL 15+, Redis 7+

set -e

echo "🚀 Starting Multi-Agent Survey Platform (Local Mode)..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Install Python 3.11+: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Check Node.js
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "Install Node.js 20+: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"

# Check PostgreSQL
echo "Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL not found${NC}"
    echo "Install PostgreSQL 15+: https://www.postgresql.org/download/"
    echo "Or use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL found${NC}"

# Check Redis
echo "Checking Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}⚠️  Redis not found${NC}"
    echo "Install Redis: https://redis.io/download"
    echo "Or use Docker: docker run -d -p 6379:6379 redis:7"
    exit 1
fi
echo -e "${GREEN}✅ Redis found${NC}"

# Setup environment
echo ""
echo "📝 Setting up environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env file. Please edit it with your settings.${NC}"
fi

# Create Python venv and install dependencies
echo ""
echo "📦 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

cd ..

# Install frontend dependencies
echo ""
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application, run these commands in separate terminals:"
echo ""
echo -e "${GREEN}Terminal 1 - Backend:${NC}"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
echo ""
echo -e "${GREEN}Terminal 2 - Frontend:${NC}"
echo "   cd frontend && npm run dev"
echo ""
echo -e "${GREEN}Terminal 3 - Celery Worker:${NC}"
echo "   cd backend && source venv/bin/activate && celery -A workers.celery_app worker --loglevel=info"
echo ""
echo "Or use tmux/pm2 to run all at once."
echo ""
echo "📱 Then open: http://localhost:3000"
