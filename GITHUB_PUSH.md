# Загрузка проекта на GitHub

## 🚀 Быстрая загрузка

### 1. Инициализация репозитория

```bash
# Перейдите в папку проекта
cd /path/to/multi-agent-survey

# Инициализируйте git
git init

# Добавьте все файлы
git add .

# Сделайте первый коммит
git commit -m "Initial commit: Multi-Agent Survey Simulation Platform"
```

### 2. Создание репозитория на GitHub

1. Откройте: https://github.com/new
2. Название: `multi-agent-survey` (или ваше)
3. Описание: `Multi-agent survey simulation platform for B2B hypothesis testing`
4. **НЕ** инициализируйте README, .gitignore или LICENSE
5. Нажмите **Create repository**

### 3. Привязка и загрузка

```bash
# Добавьте remote (замените YOUR_USERNAME на ваш ник)
git remote add origin https://github.com/VladKudr/multi-agent-survey.git

# Загрузите код
git branch -M main
git push -u origin main
```

### 4. Проверка

Откройте: https://github.com/VladKudr/multi-agent-survey

Код должен быть загружен! 🎉

---

## 🔐 Альтернатива: SSH ключ

Если используете SSH:

```bash
git remote add origin git@github.com:VladKudr/multi-agent-survey.git
git branch -M main
git push -u origin main
```

---

## 🆘 Если возникли проблемы

### Ошибка "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/VladKudr/multi-agent-survey.git
```

### Ошибка аутентификации
Используйте Personal Access Token:
1. https://github.com/settings/tokens
2. Создайте токен с правами `repo`
3. Используйте токен вместо пароля

### Ошибка "failed to push some refs"
```bash
git pull origin main --rebase
git push origin main
```

---

## 📋 После загрузки

1. **Добавьте описание** в README на GitHub
2. **Включите GitHub Actions** (если нужен CI/CD)
3. **Добавьте topics**: `fastapi`, `nextjs`, `ai`, `survey`, `multi-agent`

---

## 🎯 Развертывание (опционально)

### Railway.app
1. Зайдите на https://railway.app
2. New Project → Deploy from GitHub repo
3. Выберите ваш репозиторий
4. Готово!

### Render.com
1. https://dashboard.render.com
2. New → Blueprint
3. Подключите GitHub репозиторий

---

## 📁 Что загружено

✅ Весь код (backend, frontend)  
✅ Конфигурации Docker  
✅ Документация  
✅ Примеры агентов  

❌ НЕ загружаются (в .gitignore):
- `.env` файлы с секретами
- `node_modules/` и `venv/`
- Логи и временные файлы
