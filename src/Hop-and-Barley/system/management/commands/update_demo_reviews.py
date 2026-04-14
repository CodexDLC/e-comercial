from pathlib import Path
from typing import Any

from django.conf import settings

from codex_django.system.management.base_commands import JsonFixtureUpsertCommand


class Command(JsonFixtureUpsertCommand):
    help = "Update demo reviews from JSON fixture with hash protection"
    fixture_key = "demo_reviews"
    model_path = "reviews.Review"
    lookup_field = "id"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "features" / "reviews" / "fixtures" / "demo_reviews.json"]

    def get_defaults(self, fields: dict[str, Any]) -> dict[str, Any]:
        defaults = fields.copy()
        if "user" in defaults:
            defaults["user_id"] = defaults.pop("user")
        if "product" in defaults:
            defaults["product_id"] = defaults.pop("product")
        return defaults
