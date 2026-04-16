from pathlib import Path
from typing import Any

from codex_django.system.management.base_commands import JsonFixtureUpsertCommand
from django.conf import settings


class Command(JsonFixtureUpsertCommand):
    help = "Update orders from demo JSON fixture with hash protection"
    fixture_key = "demo_orders"
    model_path = "orders.Order"
    lookup_field = "id"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "features" / "orders" / "fixtures" / "orders.json"]

    def get_defaults(self, fields: dict[str, Any]) -> dict[str, Any]:
        defaults = fields.copy()
        if "user" in defaults:
            defaults["user_id"] = defaults.pop("user")
        return defaults
