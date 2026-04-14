# ═══════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "/cabinet/login/"
LOGIN_REDIRECT_URL = "/cabinet/"
LOGOUT_REDIRECT_URL = "/cabinet/login/"
