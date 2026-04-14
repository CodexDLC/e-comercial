from __future__ import annotations

from typing import Any

from django.core.management.base import CommandError
from django.db import transaction

from features.products.models import Category, Product


class CatalogImportService:
    """Service to handle catalog import logic."""

    @classmethod
    def build_category_map(cls, fixture_categories: list[dict[str, Any]]) -> dict[int, Category]:
        categories_by_slug = {category.slug: category for category in Category.objects.all()}
        category_map: dict[int, Category] = {}

        for entry in fixture_categories:
            fixture_pk = entry.get("pk")
            fields = entry.get("fields", {})
            slug = fields.get("slug")

            if not isinstance(fixture_pk, int) or not isinstance(slug, str):
                continue

            category = categories_by_slug.get(slug)
            if category is not None:
                category_map[fixture_pk] = category

        return category_map

    @classmethod
    def resolve_category(cls, fixture_category: Any, category_map: dict[int, Category]) -> Category:
        if not isinstance(fixture_category, int):
            raise CommandError(f"Invalid category reference in products fixture: {fixture_category!r}")

        category = category_map.get(fixture_category)
        if category is not None:
            return category

        category = Category.objects.filter(pk=fixture_category).first()
        if category is not None:
            return category

        raise CommandError(f"Category fixture reference {fixture_category} could not be resolved")

    @classmethod
    def upsert_product(
        cls, fields: dict[str, Any], category_map: dict[int, Category], lookup_field: str = "slug"
    ) -> tuple[bool, bool]:
        raw_category = fields.pop("category", None)
        if raw_category is None:
            raise CommandError("Product fixture entry is missing category")

        lookup_value = fields.get(lookup_field)
        if lookup_value in (None, ""):
            raise CommandError(f"Product fixture entry is missing {lookup_field}")

        defaults = dict(fields)
        defaults["category"] = cls.resolve_category(raw_category, category_map)

        _, created = Product.objects.update_or_create(
            **{lookup_field: lookup_value},
            defaults=defaults,
        )
        return created, not created

    @classmethod
    @transaction.atomic
    def import_products(
        cls, fixture_data: list[dict[str, Any]], fixture_categories: list[dict[str, Any]]
    ) -> tuple[int, int]:
        category_map = cls.build_category_map(fixture_categories)
        created_count = 0
        updated_count = 0

        for entry in fixture_data:
            fields = entry.get("fields", {})
            if not isinstance(fields, dict):
                raise CommandError("Invalid product fixture entry")

            created, updated = cls.upsert_product(dict(fields), category_map)
            created_count += int(created)
            updated_count += int(updated)

        return created_count, updated_count
