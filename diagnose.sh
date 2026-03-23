#!/bin/bash

echo "🔍 Диагностика подключения"
echo "=========================="
echo ""

# Check Docker containers
echo "1. Проверка Docker контейнеров:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(survey|postgres|redis)" || echo "❌ Контейнеры не найдены"
echo ""

# Check backend
echo "2. Проверка бэкенда (порт 8000):"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Бэкенд доступен"
    curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ Бэкенд НЕ доступен"
fi
echo ""

# Check frontend
echo "3. Проверка фронтенда (порт 3000):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|307"; then
    echo "✅ Фронтенд доступен"
else
    echo "❌ Фронтенд НЕ доступен"
fi
echo ""

# Check API endpoints
echo "4. Проверка API endpoints:"

# Providers endpoint
echo -n "   /api/v1/llm-config/providers: "
if curl -s http://localhost:8000/api/v1/llm-config/providers > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Health endpoint
echo -n "   /health: "
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo ""

# Test CORS
echo "5. Проверка CORS:"
CORS_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -X OPTIONS \
    http://localhost:8000/api/v1/auth/register)

if [ "$CORS_TEST" = "200" ] || [ "$CORS_TEST" = "204" ]; then
    echo "✅ CORS настроен корректно"
else
    echo "⚠️ CORS может быть не настроен (HTTP $CORS_TEST)"
fi

echo ""

# Test registration
echo "6. Тест регистрации:"
TEST_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"diag_test_'$(date +%s)'@test.com","password":"Test1234","full_name":"Diag Test","organization_name":"Diag Org","llm_provider":"kimi","llm_model":"kimi-k2","llm_api_key":"sk-test123"}' \
    -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$TEST_RESULT" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$HTTP_CODE" = "201" ]; then
    echo "✅ Регистрация работает (HTTP 201)"
elif [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️ Регистрация вернула 400 - возможно, email уже существует"
    echo "   Ответ: $(echo "$TEST_RESULT" | head -1)"
else
    echo "❌ Регистрация НЕ работает (HTTP $HTTP_CODE)"
    echo "   Ответ: $(echo "$TEST_RESULT" | head -1)"
fi

echo ""
echo "=========================="
echo ""
echo "📋 Рекомендации:"
echo ""

if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Бэкенд не доступен. Попробуйте:"
    echo "   cd infra && docker-compose restart backend"
    echo ""
fi

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Фронтенд не доступен. Попробуйте:"
    echo "   cd infra && docker-compose restart frontend"
    echo ""
fi

echo "🔗 Полезные ссылки:"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:3000"
echo ""
