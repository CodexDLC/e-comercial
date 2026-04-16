import json
from pathlib import Path
from typing import Any

from codex_django.system.management.base_commands import BaseHashProtectedCommand
from django.conf import settings
from django.core.management.base import CommandError
from django.db import transaction
from loguru import logger as log

from features.products.services.import_catalog import CatalogImportService


class Command(BaseHashProtectedCommand):
    help = "Update products from JSON fixture with hash protection"
    fixture_key = "catalog_products"
    lookup_field = "slug"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "features" / "products" / "fixtures" / "products.json"]

    def get_category_fixture_path(self) -> Path:
        return settings.BASE_DIR / "features" / "products" / "fixtures" / "categories.json"

    def load_fixture(self, fixture_path: Path) -> list[dict[str, Any]]:
        with fixture_path.open(encoding="utf-8") as fixture_file:
            data = json.load(fixture_file)

        if not isinstance(data, list):
            raise CommandError(f"Invalid fixture format in {fixture_path}")

        return data

    @transaction.atomic
    def handle_import(self, *args: Any, **options: Any) -> bool:
        log.info("Command: update_products | Action: Start")

        fixture_paths = self.get_fixture_paths()
        if not fixture_paths:
            return False

        total_created = 0
        total_updated = 0
        fixture_categories = self.load_fixture(self.get_category_fixture_path())

        for fixture_path in fixture_paths:
            fixture_data = self.load_fixture(fixture_path)
            created_count, updated_count = CatalogImportService.import_products(
                fixture_data=fixture_data,
                fixture_categories=fixture_categories,
            )
            total_created += created_count
            total_updated += updated_count

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {self.fixture_key}: {total_created} created, {total_updated} updated, 0 skipped"
            )
        )
        log.info(f"Command: update_products | Action: Success | created={total_created} | updated={total_updated}")
        return True
