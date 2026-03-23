# Быстрый старт

## Требования

- Docker Desktop (или Docker Engine + Docker Compose)
  - Windows/Mac: https://www.docker.com/products/docker-desktop
  - Linux: https://docs.docker.com/engine/install/

## Запуск

```bash
# 1. Сделать скрипты исполняемыми
chmod +x *.sh

# 2. Запустить все сервисы
./start.sh
```

Или вручную:

```bash
cd infra

# Для Docker Compose v2 (новые версии):
docker compose up -d --build

# Для Docker Compose v1 (старые версии):
docker-compose up -d --build
```

## Доступ к приложению

После запуска откройте в браузере:

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Документация API**: http://localhost:8000/docs

## Первая регистрация

1. Откройте http://localhost:3000/register
2. Заполните данные профиля
3. Выберите LLM провайдер:
   - **Kimi** (рекомендуется) - https://platform.moonshot.cn
   - OpenAI - https://platform.openai.com
   - Anthropic - https://console.anthropic.com
   - Ollama (локально) - http://localhost:11434
4. Введите API ключ
5. Завершите регистрацию

## Управление сервисами

```bash
# Проверить статус
./status.sh

# Смотреть логи всех сервисов
./logs.sh

# Смотреть логи конкретного сервиса
./logs.sh backend
./logs.sh frontend
./logs.sh postgres
./logs.sh redis

# Остановить все сервисы
./stop.sh

# Перезапустить
./stop.sh && ./start.sh
```

## Решение проблем

### Ошибка "docker-compose: command not found"

Используйте новый синтаксис:
```bash
cd infra
docker compose up -d --build
```

### Порты заняты

Если порты 3000, 8000, 5432 или 6379 заняты, измените их в `infra/docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # вместо "3000:3000"
```

### Проблемы с правами (Linux/Mac)

```bash
# Исправить права на скрипты
chmod +x *.sh

# Или запускать через bash
bash start.sh
```

## Структура проекта

```
.
├── start.sh          # Запуск сервисов
├── stop.sh           # Остановка сервисов
├── logs.sh           # Просмотр логов
├── status.sh         # Проверка статуса
├── infra/
│   └── docker-compose.yml  # Конфигурация Docker
├── backend/          # FastAPI приложение
├── frontend/         # Next.js приложение
└── agent-configs/    # Конфигурации агентов
```
