#!/bin/bash

echo "🔍 Проверка проекта Multi-Agent Survey"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        return 1
    fi
}

echo "📁 Backend структура:"
check_file "backend/main.py" "main.py"
check_file "backend/api/auth.py" "API авторизации"
check_file "backend/models/user.py" "Модели пользователя"
check_file "backend/schemas/user.py" "Схемы пользователя"
check_file "backend/test_auth.py" "Тесты авторизации"

echo ""
echo "📁 Frontend структура:"
check_file "frontend/app/login/page.tsx" "Страница входа"
check_file "frontend/app/register/page.tsx" "Страница регистрации"
check_file "frontend/app/dashboard/layout.tsx" "Layout дашборда"
check_file "frontend/middleware.ts" "Middleware защиты"
check_file "frontend/lib/api.ts" "API клиент"

echo ""
echo "📦 Docker:"
check_file "infra/docker-compose.yml" "Docker Compose"

echo ""
echo "🚀 Для запуска проекта:"
echo ""
echo "1. Запустите сервисы:"
echo "   cd infra && docker-compose up -d"
echo ""
echo "2. Проверьте API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "3. Откройте фронтенд:"
echo "   http://localhost:3000"
echo ""
echo "4. Зарегистрируйтесь и войдите"
echo ""
echo "📚 Документация API:"
echo "   http://localhost:8000/docs"
echo ""
echo "🧪 Тестирование:"
echo "   cd backend && python test_auth.py"
echo ""
