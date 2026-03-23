# Загрузка на GitHub

## 🚀 Вариант 1: Автоматический (рекомендуется)

```bash
# Выполните эту команду в папке проекта:
./push-to-github.sh
```

Скрипт автоматически:
- Инициализирует git репозиторий
- Настроит git config
- Создаст коммит
- Загрузит на GitHub

## 📝 Вариант 2: Ручной

### Шаг 1: Инициализация
```bash
cd /path/to/multi-agent-survey
git init
git add .
git commit -m "Initial commit"
```

### Шаг 2: Создайте репозиторий
1. Откройте: https://github.com/new
2. Repository name: `multi-agent-survey`
3. **НЕ** отмечайте "Initialize with README"
4. Create repository

### Шаг 3: Загрузка
```bash
git remote add origin https://github.com/VladKudr/multi-agent-survey.git
git branch -M main
git push -u origin main
```

## 🔐 Аутентификация

GitHub больше не принимает пароли. Используйте:

### Вариант A: Personal Access Token (рекомендуется)
1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Выберите scope: `repo`
4. Используйте токен вместо пароля

### Вариант B: GitHub CLI
```bash
# Установка
brew install gh  # macOS
# или
sudo apt install gh  # Ubuntu

# Авторизация
gh auth login

# Затем push
gh repo create multi-agent-survey --public --source=. --push
```

## ✅ Проверка

После загрузки откройте:
https://github.com/VladKudr/multi-agent-survey

## 🆘 Помощь

Если не получается:
1. Откройте `GITHUB_PUSH.md` - подробная инструкция
2. Используйте GitHub Desktop: https://desktop.github.com/
3. Загрузите через веб-интерфейс:
   - https://github.com/VladKudr/multi-agent-survey/upload

---

## 📁 Что будет загружено

✅ **Backend** (Python/FastAPI)
- API endpoints
- LLM Gateway с поддержкой Kimi/OpenAI/Anthropic
- Модели базы данных
- Сервисы и бизнес-логика
- Celery workers

✅ **Frontend** (Next.js/TypeScript)
- Страницы (вход, регистрация, дашборд, настройки)
- Компоненты UI
- API клиент
- Типы TypeScript

✅ **Инфраструктура**
- Docker Compose конфигурация
- Скрипты запуска
- Документация

✅ **Агенты**
- 3 примера конфигураций агентов

❌ **Не загружается** (в .gitignore):
- `.env` файлы с секретами
- `node_modules/`, `venv/`
- Временные файлы

---

## 🎯 Дальнейшие шаги

После загрузки на GitHub:

1. **Добавьте описание** репозитория на GitHub
2. **Включите Issues** для обратной связи
3. **Настройте GitHub Pages** (если нужно)
4. **Подключите CI/CD** (GitHub Actions)

---

## 🐳 Запуск после загрузки

На сервере с Docker:
```bash
git clone https://github.com/VladKudr/multi-agent-survey.git
cd multi-agent-survey
./start.sh
```

Или локально:
```bash
git clone https://github.com/VladKudr/multi-agent-survey.git
cd multi-agent-survey
./start-local.sh
```
