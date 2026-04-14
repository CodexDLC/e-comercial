"""
Test settings — used only for pytest.

Inherits from base settings but uses SQLite in-memory for speed.
"""

from pathlib import Path

from .base import *  # noqa: F403

# Base dir for templates (mirrors modules/templates.py resolution)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Enable debug mode in tests for detailed error pages
DEBUG = True

# SQLite in-memory database for fast tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# In-memory cache for tests (no Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# Disable Redis password for tests
REDIS_PASSWORD = None

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable migrations for speed (optional)
# MIGRATION_MODULES = {app: None for app in INSTALLED_APPS}

# Fast password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Explicitly set Redis host to avoid DNS issues in tests
REDIS_HOST = "localhost"

# ---------------------------------------------------------------------------
# Override TEMPLATES to remove Redis-dependent context processors.
# codex_django's site_settings and static_content processors connect to Redis
# on every request; in unit tests we use FakeRedis / in-memory cache instead.
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [_BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": ["codex_django.cabinet.templatetags.cabinet_tags"],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                # All codex_django context_processors removed for tests:
                # site_settings, static_content, seo_settings, cabinet → all use Redis
            ],
        },
    }
]
