# Установка Docker

Для запуска этого проекта требуется Docker. Выберите инструкцию для вашей системы:

## 🪟 Windows

1. Скачайте Docker Desktop:
   https://www.docker.com/products/docker-desktop

2. Установите и перезагрузите компьютер

3. Откройте PowerShell или CMD и проверьте:
   ```powershell
   docker --version
   docker compose version
   ```

## 🍎 Mac

### Через Homebrew (рекомендуется):
```bash
brew install --cask docker
```

### Или скачайте:
https://www.docker.com/products/docker-desktop

### Проверка:
```bash
docker --version
docker compose version
```

## 🐧 Linux (Ubuntu/Debian)

```bash
# Установка Docker
sudo apt update
sudo apt install -y docker.io

# Установка Docker Compose
sudo apt install -y docker-compose-plugin

# Или для старой версии:
sudo apt install -y docker-compose

# Добавить пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Перелогиниться или выполнить:
newgrp docker

# Проверка
docker --version
docker compose version
```

## 🐧 Linux (CentOS/RHEL/Fedora)

```bash
# Fedora
sudo dnf install -y docker docker-compose

# CentOS/RHEL
sudo yum install -y docker docker-compose

# Запуск службы
sudo systemctl start docker
sudo systemctl enable docker

# Проверка
docker --version
```

## 🧪 Альтернатива без Docker

Если установка Docker невозможна, можно запустить проект вручную:

### Требования:
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Запуск backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Настройте PostgreSQL и Redis
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/survey_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"
uvicorn main:app --reload --port 8000
```

### Запуск frontend:
```bash
cd frontend
npm install
npm run dev
```

### Запуск Celery worker:
```bash
cd backend
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info
```

## 🌐 Облачные альтернативы

Если локальная установка невозможна:

1. **GitHub Codespaces** - разработка в браузере
2. **GitPod** - облачная IDE
3. **Railway.app / Render.com** - деплой в облако

## ❓ Проверка установки

После установки Docker выполните:

```bash
# Должно показать версию
docker --version

# Должно показать версию compose
docker compose version

# Тестовый запуск
docker run hello-world
```

## 🆘 Проблемы?

### "Cannot connect to the Docker daemon"
```bash
# Linux - запустить службу
sudo systemctl start docker

# Или добавить в группу:
sudo usermod -aG docker $USER
# Перелогиниться!
```

### Docker Desktop не запускается (Windows)
- Включите WSL2: https://docs.microsoft.com/windows/wsl/install
- Включите виртуализацию в BIOS
- Проверьте, что Hyper-V включен

### Порт занят
```bash
# Найти процесс на порту 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Или изменить порт в infra/docker-compose.yml
```
