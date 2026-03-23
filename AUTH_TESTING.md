# Тестирование авторизации

## Быстрая проверка

### 1. Запустите сервисы
```bash
cd infra
docker-compose up -d
```

### 2. Проверьте API
```bash
# Health check
curl http://localhost:8000/health
# Должен вернуть: {"status": "healthy", "version": "1.0.0"}
```

### 3. Проверьте документацию API
Откройте http://localhost:8000/docs

Должны быть доступны эндпоинты:
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена
- `GET /api/v1/auth/me` - Информация о пользователе

## Ручное тестирование

### Регистрация
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "organization_name": "Test Org",
    "llm_provider": "kimi",
    "llm_model": "kimi-k2-07132k-preview",
    "llm_api_key": "sk-test123456789",
    "llm_temperature": 0.7,
    "llm_max_tokens": 2000
  }'
```

### Логин
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123"
```

Ответ должен содержать:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Получение информации о пользователе
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Автоматическое тестирование

### Python тест
```bash
cd backend
python test_auth.py
```

### Frontend тест
1. Откройте http://localhost:3000
2. Перейдите на /register
3. Заполните форму
4. После регистрации должен быть редирект на /dashboard

## Структура авторизации

### Backend
```
backend/
├── api/auth.py          # API endpoints (register, login, refresh, me)
├── models/user.py       # User и UserLLMConfig модели
├── schemas/user.py      # Pydantic схемы
└── test_auth.py         # Тестовый скрипт
```

### Frontend
```
frontend/
├── app/login/page.tsx         # Страница входа
├── app/register/page.tsx      # Страница регистрации
├── lib/api.ts                 # API клиент с токенами
├── middleware.ts              # Защита роутов
└── components/layout/navbar.tsx  # Навигация с выходом
```

## Безопасность

- Пароли хешируются с bcrypt
- JWT токены с TTL (access: 15 мин, refresh: 7 дней)
- CORS настроен для фронтенда
- Защита роутов через middleware

## Типичные проблемы

### "Email already registered"
Используйте уникальный email для каждого теста.

### "Could not validate credentials"
Проверьте правильность заголовка Authorization: `Bearer TOKEN`

### CORS ошибки
Убедитесь, что фронтенд URL в списке CORS_ORIGINS в .env

### База данных не инициализирована
```bash
cd infra
docker-compose down -v  # Удалить старые данные
docker-compose up -d    # Пересоздать
```
