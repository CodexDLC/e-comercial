from pathlib import Path

from codex_django.system.management.base_commands import JsonFixtureUpsertCommand
from django.conf import settings


class Command(JsonFixtureUpsertCommand):
    help = "Update users from JSON fixture with hash protection"
    fixture_key = "demo_users"
    model_path = "auth.User"
    lookup_field = "username"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "system" / "fixtures" / "demo" / "users.json"]
