# ═══════════════════════════════════════════
# Application definition
# ═══════════════════════════════════════════

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

THIRD_PARTY_APPS = [
    # Admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "django_prometheus",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
]
THIRD_PARTY_APPS.insert(0, "modeltranslation")

# ═══════════════════════════════════════════
# Codex Library Apps
# ═══════════════════════════════════════════
CODEX_APPS = [
    "codex_django.cabinet",
    "codex_django.showcase",
]

# ═══════════════════════════════════════════
# Codex Library Settings
# ═══════════════════════════════════════════
CODEX_SITE_SETTINGS_MODEL = "system.SiteSettings"
CODEX_STATIC_TRANSLATION_MODEL = "system.StaticTranslation"
CODEX_STATIC_PAGE_SEO_MODEL = "system.StaticPageSeo"

LOCAL_APPS = [
    "core",
    "system",
    "features.main",
    "features.products",
    "features.orders",
    "features.reviews",
    "cabinet",
    "features.conversations",
]

INSTALLED_APPS = LOCAL_APPS + CODEX_APPS + THIRD_PARTY_APPS + DJANGO_APPS
