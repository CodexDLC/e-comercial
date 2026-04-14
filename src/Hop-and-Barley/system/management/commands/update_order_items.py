from pathlib import Path
from typing import Any

from django.conf import settings

from codex_django.system.management.base_commands import JsonFixtureUpsertCommand


class Command(JsonFixtureUpsertCommand):
    help = "Update order items from demo JSON fixture with hash protection"
    fixture_key = "demo_order_items"
    model_path = "orders.OrderItem"
    lookup_field = "id"

    def get_fixture_paths(self) -> list[Path]:
        return [settings.BASE_DIR / "features" / "orders" / "fixtures" / "order_items.json"]

    def get_defaults(self, fields: dict[str, Any]) -> dict[str, Any]:
        defaults = fields.copy()
        if "order" in defaults:
            defaults["order_id"] = defaults.pop("order")
        if "product" in defaults:
            defaults["product_id"] = defaults.pop("product")
        return defaults
