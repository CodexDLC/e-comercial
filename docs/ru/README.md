# Русская документация 🇷🇺

Добро пожаловать в проект **Hop and Barley**. Здесь вы найдете информацию об установке, процессе разработки и функциональных возможностях проекта.

## 🛠 Установка

### 1. Docker (Рекомендуется)
Запуск всей инфраструктуры (БД, Redis, Backend, Nginx):
```bash
docker compose -f deploy/docker-compose.yml up --build
```
*Проект будет доступен по адресу: [http://localhost:8080](http://localhost:8080)*

### 2. Локальный запуск
Используя `uv` или `pip`:
```bash
uv sync
python src/Hop-and-Barley/manage.py migrate
python src/Hop-and-Barley/manage.py startserver
```

## 🧪 Процесс разработки

### Контроль качества (Quality Gate)
Единый скрипт для запуска всех проверок (линтеры, типы, безопасность):
```bash
python tools/dev/check.py
```

### Ручные команды
- **Линтинг**: `ruff check .`
- **Проверка типов**: `mypy src/Hop-and-Barley`
- **Тесты**: `pytest`

## 🔗 Быстрые ссылки
- [Функционал проекта](features.md)
- [API Документация](http://localhost:8080/api/v1/docs/)
- [Главный индекс](../index.md)
