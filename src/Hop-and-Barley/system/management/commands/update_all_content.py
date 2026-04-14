from typing import ClassVar

from codex_django.system.management.base_commands import BaseUpdateAllContentCommand


class Command(BaseUpdateAllContentCommand):
    """
    Run all content update commands and clear cache.
    Useful to run during entrypoint initialization or deployments.
    """

    help = "Run all content update commands and clear cache"

    commands_to_run: ClassVar[list[str]] = [
        "update_site_settings",
        "update_categories",
        "update_products",
        "update_users",
        "update_orders",
        "update_order_items",
        "update_reviews",
        "update_demo_reviews",
    ]
