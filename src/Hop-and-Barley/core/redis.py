try:
    from codex_django.core.redis import get_default_redis_manager
except ImportError:  # pragma: no cover - compatibility for older codex-django installs
    from codex_django.core.redis.managers.base import BaseDjangoRedisManager

    redis_manager = BaseDjangoRedisManager()
else:
    redis_manager = get_default_redis_manager()
