# Hop and Barley — Интернет-магазин крафтового пива 🍻

Добро пожаловать в **Hop and Barley** — современную платформу электронной коммерции для любителей крафтового пива. Проект построен на базе Django 6 с использованием передовых инструментов для быстрой и качественной разработки.

## 🚀 Основные возможности

- 🛒 **Умная корзина**: Изменение количества товаров "на лету", проверка остатков на складе.
- 📦 **Каталог товаров**: Удобная фильтрация по категориям, полнотекстовый поиск и сортировка.
- 💬 **Система отзывов**: Честный рейтинг от реальных покупателей.
- 🔐 **Безопасность**: JWT-аутентификация для API и интеграция с `django-allauth`.
- 📊 **Кабинет управления**: Мощная панель для сотрудников (Staff) и личный кабинет клиента.
- 📱 **Современный UI**: Динамические интерфейсы на HTMX и Alpine.js без перегрузки страниц.

## 🛠 Технологический стек

- **Backend**: Django 6, REST Framework, [codex-django](https://github.com/codex-team/codex-django) (библиотека-скелет).
- **Frontend**: Vanilla CSS (CSS Variables), HTMX, Alpine.js (минималистичный JS).
- **Инфраструктура**: PostgreSQL, Redis (кэш/сессии), Docker + Compose.
- **Инструменты**: Ruff (линтинг), Mypy (типизация), Pytest (тестирование).

---

## ⚡ Быстрый старт

### 1. Подготовка окружения

Склонируйте репозиторий и создайте файл настроек:

```bash
cp .env.example .env
```

### 2. Запуск через Docker (Рекомендуется)

Весь стек (БД, Redis, Backend, Nginx) поднимается одной командой:

```bash
docker compose -f deploy/docker-compose.yml up --build
```

*Проект будет доступен по адресу: [http://localhost:8080](http://localhost:8080)*

### 3. Локальная разработка

Если вы используете `uv` или `pip`:

```bash
uv sync
python src/Hop-and-Barley/manage.py migrate
python src/Hop-and-Barley/manage.py startserver
```

---

## 🎨 Работа с фронтендом и ассетами

Для работы с CSS/JS в проекте используются специальные команды `codex-django`:

- `python manage.py startserver` — Запуск сервера вместе с компиляцией статики.
- `python manage.py dev` — Режим разработки с авто-обновлением (watch) ассетов.
- `python manage.py compile_assets` — Разовая сборка всех ресурсов для продакшена.

---

## 📐 Структура проекта

```text
src/Hop-and-Barley/
├── core/           # Конфигурация проекта (settings, urls)
├── features/       # Бизнес-логика (products, orders, reviews)
├── system/         # Системные модули (SEO, профили, логирование)
├── cabinet/        # Интерфейсы личных кабинетов
└── templates/      # Глобальные HTML-шаблоны
```

---

## 🔌 API Документация

Проект предоставляет полноценный REST API с автоматической документацией Swagger:

🔗 **URL**: `http://localhost:8080/api/v1/docs/`

### Примеры запросов

#### Список продуктов

```bash
curl http://localhost:8080/api/v1/products/
```

#### Получение токена (JWT)

```bash
curl -X POST http://localhost:8080/api/v1/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'
```

---

## 🧪 Тестирование и качество

Мы используем комплексный подход к обеспечению качества кода.

### 1. Единый "Quality Gate" (Checker)

В проекте настроен скрипт, который прогоняет сразу все проверки (линтеры, типы, безопасность, тесты) согласно правилам из `pyproject.toml`:

```bash
python tools/dev/check.py
```

### 2. Pre-commit Hooks

Для автоматической проверки кода перед каждым коммитом настроен `pre-commit`. Он запускает `ruff`, `markdownlint`, `bandit`, `pip-audit`, проверку секретов и Docker-файлов.

Установка и запуск:

```bash
pre-commit install
pre-commit run --all-files
```

### 3. Ручной запуск инструментов

- **Линтинг**: `ruff check .`
- **Типизация**: `mypy src/Hop-and-Barley`
- **Тесты**: `pytest`

---

Разработано с ❤️ в качестве тестового проекта по окончании модуля.
