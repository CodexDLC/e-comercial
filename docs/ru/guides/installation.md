# Инструкция по установке 🛠

Этот гайд поможет вам настроить окружение для разработки проекта Hop and Barley.

## 📦 Предварительные требования
- Python 3.12+
- Docker и Docker Compose (рекомендуется)
- `uv` (рекомендуемый менеджер пакетов)

## 🐳 Запуск через Docker (Рекомендуется)
Самый быстрый способ запустить весь стек (БД, Redis, Backend, Nginx):
```bash
# Клонируйте и настройте окружение
cp .env.example .env

# Запустите проект
docker compose -f deploy/docker-compose.yml up --build
```
*Адрес проекта: [http://localhost:8080](http://localhost:8080)*

## 🐍 Локальный запуск
Если вы предпочитаете запуск без Docker:

### 1. Установка зависимостей
```bash
uv sync
```

### 2. Настройка окружения
Создайте файл `.env` на основе `.env.example` и укажите данные для подключения к вашей локальной БД и Redis.

### 3. Инициализация БД
```bash
python src/Hop-and-Barley/manage.py migrate
python src/Hop-and-Barley/manage.py createsuperuser
```

### 4. Запуск сервера
```bash
python src/Hop-and-Barley/manage.py startserver
```

## 🔐 Переменные окружения
Основные переменные в `.env`:
- `DJANGO_SECRET_KEY`: Ключ безопасности.
- `DATABASE_URL`: Строка подключения к БД.
- `REDIS_URL`: Ссылка на Redis для сессий и кэша.
- `CART_SESSION_ID`: Идентификатор корзины в сессии.
