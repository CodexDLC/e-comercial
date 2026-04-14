import os
from pathlib import Path


def _discover_project_root() -> Path:
    """Find the workspace root without depending on the import location."""
    markers = ("pyproject.toml", ".git", "manage.py")

    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for candidate in (start, *start.parents):
            if any((candidate / marker).exists() for marker in markers):
                return candidate

    return Path("/app") if os.environ.get("IS_DOCKER", "False").lower() in ("true", "1", "t") else Path.cwd()


def _default_log_dir() -> Path:
    """Resolve logs under the workspace locally and under /app in Docker."""
    project_root = _discover_project_root()

    if os.environ.get("IS_DOCKER", "False").lower() in ("true", "1", "t"):
        return project_root / "logs"

    return project_root / "logs"


# ═══════════════════════════════════════════
# Logging (codex-core compatible)
# ═══════════════════════════════════════════

# Loguru / codex-core compatible fields (used in core/logger.py)
LOG_LEVEL_CONSOLE = os.environ.get("LOG_LEVEL_CONSOLE", "INFO")
LOG_LEVEL_FILE = os.environ.get("LOG_LEVEL_FILE", "DEBUG")
LOG_ROTATION = os.environ.get("LOG_ROTATION", "10 MB")
LOG_DIR = os.environ.get("LOG_DIR", str(_default_log_dir()))

# Standard Django LOGGING (fallback if loguru is disabled/missing)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL_CONSOLE,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
