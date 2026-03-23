# Исправления для сборки

## Выполненные исправления

### 1. Backend - Python зависимости
**Проблема:** Конфликт версий с torch/transformers

**Решение:** 
- Убраны тяжелые NLP-зависимости из `requirements.txt`
- Создан отдельный `requirements-nlp.txt` для опциональной установки
- Исправлен `nlp_service.py` - работает без тяжелых зависимостей

### 2. Frontend - недостающие компоненты
**Проблема:** Отсутствовали компоненты shadcn/ui

**Решение:**
- Добавлен `components/ui/input.tsx`
- Добавлен `components/ui/select.tsx`
- Добавлен `components/ui/label.tsx`
- Добавлен `lib/icons.tsx` для иконок
- Исправлен `lib/api.ts` - импорты перенесены в начало файла

## Команды для обновления репозитория

```bash
cd /path/to/multi-agent-survey

# Добавить все изменения
git add .

# Создать коммит
git commit -m "Fix: Remove heavy NLP deps, add missing UI components

- Move torch/transformers to optional requirements-nlp.txt
- Make NLP service work without heavy dependencies
- Add missing shadcn/ui components (Input, Select, Label)
- Fix api.ts imports"

# Push на GitHub
git push origin main
```

## Проверка сборки OpenClaw

После push сборка должна пройти успешно:
1. Backend установится без ошибок (без torch)
2. Frontend найдет все компоненты

Если нужны NLP функции (BERTopic), установите дополнительно:
```bash
pip install -r requirements.txt -r requirements-nlp.txt
```
