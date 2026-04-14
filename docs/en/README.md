# English Documentation 🇬🇧

Welcome to the English documentation for **Hop and Barley**. This guide covers installation, development workflow, and core project features.

## 🛠 Installation

### 1. Docker (Recommended)
The entire stack (DB, Redis, Backend, Nginx) can be started with a single command:
```bash
docker compose -f deploy/docker-compose.yml up --build
```
*Access the project at: [http://localhost:8080](http://localhost:8080)*

### 2. Local Setup
Using `uv` or `pip`:
```bash
uv sync
python src/Hop-and-Barley/manage.py migrate
python src/Hop-and-Barley/manage.py startserver
```

## 🧪 Development Workflow

### Quality Gate
We use a unified checker to run all linters, type checks, and security audits:
```bash
python tools/dev/check.py
```

### Manual Commands
- **Linting**: `ruff check .`
- **Type Checking**: `mypy src/Hop-and-Barley`
- **Testing**: `pytest`

## 🔗 Quick Links
- [Project Features](features.md)
- [API Reference](http://localhost:8080/api/v1/docs/)
- [Main Index](../index.md)
