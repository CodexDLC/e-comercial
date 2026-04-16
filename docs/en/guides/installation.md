# Installation Guide 🛠

This guide helps you set up the development environment for Hop and Barley.

## 📦 Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional but recommended)
- `uv` (recommended package manager)

## 🐳 Docker Setup (Recommended)
The fastest way to get the project running with all dependencies (DB, Redis, Nginx):
```bash
# Clone and copy env
cp .env.example .env

# Start the stack
docker compose -f deploy/docker-compose.yml up --build
```
*Project URL: [http://localhost:8080](http://localhost:8080)*

## 🐍 Local Setup
If you prefer running without Docker:

### 1. Synchronize Dependencies
```bash
uv sync
```

### 2. Configure Environment
Create a `.env` file based on `.env.example` and set your local database/Redis credentials.

### 3. Database Initialization
```bash
python src/Hop-and-Barley/manage.py migrate
python src/Hop-and-Barley/manage.py createsuperuser
```

### 4. Run Development Server
```bash
python src/Hop-and-Barley/manage.py startserver
```

## 🔐 Environment Variables
Key variables in `.env`:
- `DJANGO_SECRET_KEY`: Security key.
- `DATABASE_URL`: Connection string (e.g., `postgres://user:pass@localhost:5432/db`). # pragma: allowlist secret
- `REDIS_URL`: Cache and session store.
- `CART_SESSION_ID`: Identifier for the session-based cart.
