# Multi-Agent Survey Simulation Platform

Платформа для симуляции B2B-опросов с использованием AI-агентов, представляющих различные типы компаний (ИП и ООО) с реалистичными персонами и характеристиками.

## Возможности

- **AI-Агенты**: Готовые персоны с детальными профилями (тип собственности, отрасль, размер, болевые точки, стиль принятия решений)
- **Опросы**: Создание количественных (шкалы Лайкерта) и качественных (открытые вопросы) исследований
- **Симуляции**: Параллельное выполнение опросов множеством агентов через Celery
- **Аналитика**: NLP-анализ ответов с помощью BERTopic и spaCy
- **Мультиарендность**: Изоляция данных по организациям
- **Пользовательские LLM**: Каждый пользователь может использовать свой API ключ и модель (Kimi, OpenAI, Anthropic, Ollama)

## Технологический стек

- **Frontend**: Next.js 14+, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy
- **База данных**: PostgreSQL 15+
- **Очередь задач**: Celery + Redis
- **LLM Gateway**: LiteLLM с поддержкой пользовательских конфигураций
- **NLP**: spaCy, BERTopic
- **Контейнеризация**: Docker + Docker Compose

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- API ключ для LLM провайдера (рекомендуется Kimi/Moonshot AI)

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd multi-agent-survey
```

2. Создайте `.env` файл на основе примера:
```bash
cp .env.example .env
# Можно оставить значения по умолчанию для локального запуска
```

3. Запустите сервисы:
```bash
cd infra
docker-compose up -d
```

4. Откройте фронтенд: http://localhost:3000

5. Зарегистрируйтесь, указав:
   - Ваши данные (email, пароль, ФИО)
   - Название организации
   - LLM провайдер и API ключ (рекомендуется Kimi)

### Получение API ключа Kimi

1. Зарегистрируйтесь на https://platform.moonshot.cn
2. Создайте API ключ в личном кабинете
3. Используйте ключ при регистрации на платформе

## Настройка LLM

Каждый пользователь может настроить свой LLM провайдер:

1. **Kimi (Moonshot AI)** - рекомендуется
   - Базовый URL: `https://api.moonshot.cn/v1`
   - Модели: `kimi-k2-07132k-preview`, `kimi-latest`, `kimi-k1.5`
   - Поддерживает длинный контекст до 2M токенов

2. **OpenAI**
   - Модели: `gpt-4`, `gpt-4-turbo`, `gpt-4o`, `gpt-3.5-turbo`

3. **Anthropic Claude**
   - Модели: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`

4. **Ollama (локальные модели)**
   - Для локального развертывания

5. **Custom (OpenAI-compatible)**
   - Другие провайдеры с OpenAI-compatible API

## API документация

После запуска сервиса документация доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные эндпоинты

```
POST   /api/v1/auth/register          # Регистрация с LLM настройками
POST   /api/v1/auth/login             # Авторизация
GET    /api/v1/auth/me                # Информация о текущем пользователе

GET    /api/v1/llm-config/providers   # Список доступных провайдеров
GET    /api/v1/llm-config/me          # Получить настройки LLM
POST   /api/v1/llm-config/me          # Создать настройки LLM
PATCH  /api/v1/llm-config/me          # Обновить настройки LLM
POST   /api/v1/llm-config/me/test     # Проверить подключение к LLM

GET    /api/v1/agents                 # Список агентов
GET    /api/v1/surveys                # Список опросов
POST   /api/v1/simulations            # Запустить симуляцию
```

## Структура проекта

```
/frontend          # Next.js приложение
  /app
    /login         # Страница входа
    /register      # Страница регистрации с настройками LLM
    /settings/llm  # Настройки LLM
/backend           # FastAPI приложение
  /api
    /auth.py       # Авторизация и регистрация
    /llm_config.py # Управление LLM настройками
  /services
    /llm_config_service.py  # Сервис для работы с LLM конфигурациями
  /llm
    /gateway.py    # LLM Gateway с поддержкой пользовательских конфигов
/agent-configs     # YAML конфиги агентов
```

## Конфигурация агентов

Агенты определяются в YAML-файлах в директории `agent-configs/`:

```yaml
agent:
  id: "unique-id"
  legal_type: "ООО" | "ИП"
  company_name: "Название"
  industry: "Отрасль"
  size: "micro" | "SMB" | "mid" | "enterprise"
  region: "Город"
  decision_maker:
    role: "Должность"
    age: 42
    gender: "male" | "female"
    education: "Образование"
    mbti: "INTJ"
    risk_appetite: "low" | "medium" | "high"
    communication_style: "formal" | "informal" | "mixed"
  pain_points:
    - "Болевая точка 1"
  values:
    - "Ценность 1"
  budget_sensitivity: "low" | "medium" | "high"
  digital_maturity: 1-5
```

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Тестирование

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Миграции базы данных

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Безопасность

- API ключи пользователей хранятся в базе данных (в production рекомендуется шифрование)
- Каждый пользователь использует только свой API ключ
- Поддержка rate limiting на уровне пользователя
- JWT токены с коротким сроком жизни (access: 15 мин, refresh: 7 дней)

## Лицензия

MIT
