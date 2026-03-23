#!/bin/bash

# Script to push project to GitHub
# Usage: ./push-to-github.sh [repository-name]

set -e

REPO_NAME="${1:-multi-agent-survey}"
GITHUB_USER="VladKudr"

echo "🚀 Подготовка к загрузке на GitHub..."
echo ""
echo "📁 Репозиторий: $GITHUB_USER/$REPO_NAME"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен!"
    echo "Установите Git: https://git-scm.com/downloads"
    exit 1
fi

# Check if already initialized
if [ -d ".git" ]; then
    echo "⚠️  Git репозиторий уже инициализирован"
    read -p "Продолжить с текущим репозиторием? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "🔧 Инициализация git репозитория..."
    git init
    git branch -M main
fi

# Configure git if not set
if ! git config --get user.name &> /dev/null; then
    echo ""
    read -p "Введите ваше имя для git: " git_name
    git config user.name "$git_name"
fi

if ! git config --get user.email &> /dev/null; then
    echo ""
    read -p "Введите ваш email для git: " git_email
    git config user.email "$git_email"
fi

# Add all files
echo ""
echo "📦 Добавление файлов..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "✅ Нет изменений для коммита"
else
    echo "💾 Создание коммита..."
    git commit -m "Initial commit: Multi-Agent Survey Simulation Platform

Features:
- Multi-agent simulation with AI personas
- Support for Kimi, OpenAI, Anthropic, Ollama
- Custom LLM configuration per user
- Quantitative and qualitative surveys
- Real-time simulation progress
- NLP analytics with BERTopic

Tech Stack:
- Backend: FastAPI, Python 3.11+
- Frontend: Next.js 14+, TypeScript
- Database: PostgreSQL 15+
- Queue: Celery + Redis
- Containerization: Docker"
fi

# Check remote
if git remote get-url origin &> /dev/null; then
    echo ""
    echo "⚠️  Remote 'origin' уже настроен:"
    git remote get-url origin
    read -p "Обновить remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    fi
else
    echo ""
    echo "🔗 Добавление remote..."
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi

echo ""
echo "📤 Загрузка на GitHub..."
echo ""

# Try to push
if git push -u origin main; then
    echo ""
    echo "✅ УСПЕХ! Проект загружен на GitHub!"
    echo ""
    echo "🌐 Откройте: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
else
    echo ""
    echo "❌ Ошибка загрузки"
    echo ""
    echo "Возможные причины:"
    echo "1. Репозиторий не создан на GitHub"
    echo "2. Неправильные учетные данные"
    echo "3. Нет доступа к репозиторию"
    echo ""
    echo "Решение:"
    echo "1. Создайте репозиторий: https://github.com/new"
    echo "2. Используйте Personal Access Token вместо пароля"
    echo "3. Проверьте права доступа"
    echo ""
    echo "Инструкция: GITHUB_PUSH.md"
    exit 1
fi
