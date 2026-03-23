# Начало работы

## ⚠️ У вас не установлен Docker!

Вы получили ошибку `command not found: docker`. Есть несколько вариантов решения:

## Вариант 1: Установить Docker (рекомендуется)

### Windows/Mac
Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# Перелогинитесь!
```

Подробнее см. [INSTALL_DOCKER.md](INSTALL_DOCKER.md)

После установки:
```bash
./start.sh
```

---

## Вариант 2: Запуск без Docker (сложнее)

### Требования:
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Проверка окружения:
```bash
./check-env.sh
```

### Настройка и запуск:
```bash
./start-local.sh
```

Этот скрипт проверит зависимости и настроит проект.

Затем запустите в 3 разных терминалах:

```bash
# Терминал 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Терминал 2 - Frontend  
cd frontend
npm run dev

# Терминал 3 - Celery Worker
cd backend
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info
```

---

## Вариант 3: Облачные IDE (быстрый старт)

### GitHub Codespaces
1. Загрузите проект на GitHub
2. Нажмите "Code" → "Codespaces" → "Create codespace"
3. Docker уже установлен - просто запустите `./start.sh`

### GitPod
1. Откройте: https://gitpod.io/#https://github.com/YOUR_REPO
2. Docker доступен по умолчанию

---

## Вариант 4: Бесплатный облачный хостинг

### Railway.app (рекомендуется)
1. Зарегистрируйтесь: https://railway.app
2. Подключите GitHub репозиторий
3. Railway автоматически развернет все сервисы

### Render.com
1. Зарегистрируйтесь: https://render.com
2. Создайте Blueprint из `render.yaml`

---

## Проверка после запуска

Откройте в браузере:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Регистрация

1. Откройте http://localhost:3000/register
2. Заполните профиль
3. Выберите LLM провайдер и введите API ключ:
   - **Kimi**: https://platform.moonshot.cn
   - **OpenAI**: https://platform.openai.com
   - **Anthropic**: https://console.anthropic.com

## Команды управления

```bash
# Проверить окружение
./check-env.sh

# Запуск (требуется Docker)
./start.sh

# Остановка
./stop.sh

# Логи
./logs.sh

# Статус
./status.sh

# Локальный запуск (без Docker)
./start-local.sh
```

## Нужна помощь?

1. Проверьте [README.md](README.md) - полная документация
2. Проверьте [INSTALL_DOCKER.md](INSTALL_DOCKER.md) - установка Docker
3. Откройте issue на GitHub
