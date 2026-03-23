#!/bin/bash

echo "🔍 Проверка окружения..."
echo ""

# Check OS
echo "💻 Операционная система:"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   Linux detected"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "   Distribution: $NAME $VERSION"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   macOS detected"
    sw_vers -productVersion 2>/dev/null || true
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "   Windows detected"
fi
echo ""

# Check Docker
echo "🐳 Docker:"
if command -v docker &> /dev/null; then
    echo "   ✅ Docker installed: $(docker --version)"
    
    # Check if Docker is running
    if docker info &> /dev/null; then
        echo "   ✅ Docker is running"
    else
        echo "   ❌ Docker is installed but not running!"
        echo "      Start Docker Desktop or run: sudo systemctl start docker"
    fi
    
    # Check Docker Compose
    if docker compose version &> /dev/null; then
        echo "   ✅ Docker Compose v2: $(docker compose version --short)"
    elif docker-compose version &> /dev/null; then
        echo "   ✅ Docker Compose v1: $(docker-compose version --short)"
    else
        echo "   ⚠️  Docker Compose not found"
    fi
else
    echo "   ❌ Docker NOT installed!"
    echo ""
    echo "   📥 Установите Docker:"
    echo "      • Windows/Mac: https://www.docker.com/products/docker-desktop"
    echo "      • Ubuntu: sudo apt install docker.io docker-compose"
    echo "      • Mac (Homebrew): brew install --cask docker"
fi
echo ""

# Check ports
echo "🔌 Проверка портов:"
ports=("3000" "8000" "5432" "6379")
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || \
       netstat -tuln 2>/dev/null | grep -q ":$port " || \
       ss -tuln 2>/dev/null | grep -q ":$port " ; then
        echo "   ⚠️  Port $port is already in use"
    else
        echo "   ✅ Port $port is free"
    fi
done
echo ""

# Memory
echo "💾 Память:"
if command -v free &> /dev/null; then
    free -h | grep "Mem:"
elif command -v vm_stat &> /dev/null; then
    vm_stat | head -5
else
    echo "   Cannot determine memory"
fi
echo ""

# Disk space
echo "💿 Диск:"
df -h . 2>/dev/null | tail -1 || echo "   Cannot determine disk space"
echo ""

# Summary
echo "📋 Результат:"
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "   ✅ Система готова к запуску!"
    echo ""
    echo "   Запустите проект:"
    echo "      ./start.sh"
else
    echo "   ❌ Требуется установка Docker"
    echo ""
    echo "   См. инструкции: INSTALL_DOCKER.md"
    echo "   Или онлайн: https://docs.docker.com/get-docker/"
fi
