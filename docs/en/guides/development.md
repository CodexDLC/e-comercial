# Development Workflow 🧪

We maintain high code quality standards through automated tools and strict checks.

## 🛡️ Quality Gate (Checker)
The project includes a unified script to run all code quality tools:
```bash
python tools/dev/check.py
```
This script runs:
1. **Linter**: `ruff` for code style.
2. **Type Checker**: `mypy` for static analysis.
3. **Security**: `bandit` for vulnerability checks.
4. **Secrets**: `detect-secrets` for leaked credentials.
5. **Tests**: `pytest` for functional verification.

## 🧪 Testing
We use `pytest` for unit and integration tests.
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html
```

## 📐 Migrations
When changing models, always use the standard Django workflow:
```bash
python src/Hop-and-Barley/manage.py makemigrations
python src/Hop-and-Barley/manage.py migrate
```

## 🎨 Asset Management
Static assets (CSS/JS) are handled by `codex-django`:
- `python manage.py dev`: Auto-compiles assets during development.
- `python manage.py compile_assets`: Builds assets for production.
