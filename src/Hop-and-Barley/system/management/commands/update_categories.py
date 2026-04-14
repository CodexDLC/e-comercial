from pathlib import Path
from django.conf import settings
from codex_django.system.management.base_commands import JsonFixtureUpsertCommand

class Command(JsonFixtureUpsertCommand):
    help = "Update categories from JSON fixture with hash protection"
    fixture_key = "catalog_categories"
    model_path = "products.Category"
    lookup_field = "slug"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "features" / "products" / "fixtures" / "categories.json"]
