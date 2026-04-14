import os
import pytest
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

@pytest.mark.unit
class TestCoreSmoke:
    """Smoke tests to ensure core modules are importable and basic functionality works."""
    
    def test_redis_manager_importable(self):
        from core.redis import redis_manager
        assert redis_manager is not None

    def test_asgi_application(self, monkeypatch):
        monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "core.settings.test")
        application = get_asgi_application()
        assert application is not None

    def test_wsgi_application(self, monkeypatch):
        monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "core.settings.test")
        application = get_wsgi_application()
        assert application is not None

    def test_settings_importable(self):
        from core.settings import base, dev, prod, test
        assert base.SECRET_KEY is not None
        assert test.SECRET_KEY is not None
        # dev and prod might fail if env vars missing, but they should be importable
        assert dev is not None
        assert prod is not None

    def test_api_urls_importable(self):
        from core.api_urls import urlpatterns
        assert len(urlpatterns) > 0

    def test_sitemaps_importable(self):
        from core.sitemaps import sitemaps
        assert sitemaps is not None
