import os
from pathlib import Path

from codex_django.core.i18n.discovery import discover_locale_paths

# Root of Django project: src/backend_django
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# ═══════════════════════════════════════════
# Internationalization
# ═══════════════════════════════════════════

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en")
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ("en", "English"),
    ("ru", "Russian"),
]

try:
    import modeltranslation  # noqa

    MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE.split("-")[0]
    MODELTRANSLATION_LANGUAGES = (
        "en",
        "ru",
    )
except ImportError:
    pass

LOCALE_PATHS = discover_locale_paths(BASE_DIR)
