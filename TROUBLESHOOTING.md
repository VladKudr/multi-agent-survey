# Решение проблемы "Failed to fetch"

## 🔴 Причина
"Failed to fetch" означает, что фронтенд (порт 3000) не может подключиться к бэкенду (порт 8000).

## ✅ Решения

### 1. Проверьте, что сервисы запущены

```bash
cd infra
docker-compose ps
```

Должно показать 5 контейнеров: postgres, redis, backend, celery_worker, frontend

Если какой-то не запущен:
```bash
docker-compose logs backend  # Посмотреть ошибки бэкенда
docker-compose logs frontend # Посмотреть ошибки фронтенда
```

### 2. Проверьте CORS настройки

Проверьте файл `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Добавьте оба
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Проверьте API_URL

В `frontend/lib/api.ts` должно быть:
```typescript
const API_URL = "http://localhost:8000/api/v1";
```

Если вы используете IP вместо localhost:
```typescript
const API_URL = "http://192.168.1.100:8000/api/v1";  # Ваш IP
```

### 4. Проверьте вручную

```bash
# Проверьте бэкенд
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/llm-config/providers

# Проверьте из браузера
# Откройте http://localhost:8000/docs - должна загрузиться документация API
```

### 5. Пересоберите проект

```bash
cd infra
docker-compose down -v
docker-compose up -d --build
```

### 6. Проверьте логи в реальном времени

```bash
# В одном терминале
cd infra && docker-compose logs -f backend

# В другом терминале
cd infra && docker-compose logs -f frontend
```

## 🧪 Быстрый тест

Выполните в терминале:
```bash
# 1. Проверьте, что бэкенд отвечает
curl -s http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend не отвечает"

# 2. Проверьте провайдеров
curl -s http://localhost:8000/api/v1/llm-config/providers && echo "✅ API OK" || echo "❌ API не доступен"

# 3. Проверьте регистрацию
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test123@test.com","password":"Test1234","full_name":"Test","organization_name":"Test","llm_provider":"kimi","llm_model":"kimi-k2","llm_api_key":"sk-test"}'
```

## 🔧 Частые ошибки

### "Connection refused"
Бэкенд не запущен или слушает другой порт.

### "CORS error"
Нужно настроить CORS в `backend/main.py`.

### "Network Error"
Фаервол или Docker network issues.

## 🆘 Если ничего не помогает

1. Остановите всё:
```bash
cd infra
docker-compose down -v
docker system prune -f
```

2. Пересоберите заново:
```bash
docker-compose up -d --build
```

3. Проверьте:
```bash
# Бэкенд
http://localhost:8000/health

# Фронтенд  
http://localhost:3000

# API Docs
http://localhost:8000/docs
```
