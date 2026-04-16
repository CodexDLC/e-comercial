from pathlib import Path

from codex_django.system.management.base_commands import SingletonFixtureUpdateCommand
from django.conf import settings


class Command(SingletonFixtureUpdateCommand):
    """
    Load Site Settings from JSON fixture into the SiteSettings singleton.

    Usage: python manage.py update_site_settings [--force]
    Fixture: system/fixtures/content/site_settings.json
    """

    help = "Update Site Settings from JSON fixture (system/fixtures/content/site_settings.json)"
    fixture_key = "site_settings"
    model_path = "system.SiteSettings"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "system" / "fixtures" / "content" / "site_settings.json"]
