"""Integration tests for the update_products management command."""

import json

import pytest

from features.products.models import Category, Product
from features.products.services.import_catalog import CatalogImportService
from system.management.commands.update_products import Command

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def _write_category_fixture(tmp_path, pk, name, slug):
    fixture_path = tmp_path / "categories.json"
    fixture_path.write_text(
        json.dumps([
            {
                "model": "products.category",
                "pk": pk,
                "fields": {"name": name, "slug": slug},
            }
        ]),
        encoding="utf-8",
    )
    return fixture_path


def test_upsert_product_resolves_category_from_fixture_slug(tmp_path):
    fixture_path = _write_category_fixture(tmp_path, 1, "Hops", "hops")
    Category.objects.create(name="Stored hops", slug="hops")
    command = Command()
    command.get_category_fixture_path = lambda: fixture_path

    fixture_categories = command.load_fixture(fixture_path)
    category_map = CatalogImportService.build_category_map(fixture_categories)

    created, updated = CatalogImportService.upsert_product(
        {
            "category": 1,
            "name": "Citra Hops",
            "slug": "citra-hops",
            "description": "Bright citrus aroma.",
            "price": "5.99",
            "stock": 100,
            "is_active": True,
            "order": 1,
            "specifications": {},
        }.copy(),
        category_map,
    )

    product = Product.objects.get(slug="citra-hops")
    assert created is True
    assert updated is False
    assert product.category.slug == "hops"


def test_upsert_product_updates_existing_product(tmp_path):
    """upsert_product should update price/stock on second call."""
    fixture_path = _write_category_fixture(tmp_path, 2, "Malt", "malt")
    Category.objects.create(name="Malt", slug="malt")
    command = Command()
    command.get_category_fixture_path = lambda: fixture_path

    fixture_categories = command.load_fixture(fixture_path)
    category_map = CatalogImportService.build_category_map(fixture_categories)

    payload = {
        "category": 2,
        "name": "Pale Malt",
        "slug": "pale-malt",
        "description": "Base malt.",
        "price": "3.00",
        "stock": 50,
        "is_active": True,
        "order": 1,
        "specifications": {},
    }
    CatalogImportService.upsert_product(payload.copy(), category_map)

    # Second call with updated price
    payload["price"] = "4.00"
    created, updated = CatalogImportService.upsert_product(payload.copy(), category_map)

    product = Product.objects.get(slug="pale-malt")
    assert created is False
    assert updated is True
    assert str(product.price) == "4.00"


def test_upsert_product_skips_unknown_category(tmp_path):
    """Upsert should skip (return False, False) when category not found."""
    fixture_path = _write_category_fixture(tmp_path, 99, "Ghost", "ghost")
    command = Command()
    command.get_category_fixture_path = lambda: fixture_path

    fixture_categories = command.load_fixture(fixture_path)
    category_map = CatalogImportService.build_category_map(fixture_categories)

    from django.core.management.base import CommandError
    with pytest.raises(CommandError, match="could not be resolved"):
        CatalogImportService.upsert_product(
            {
                "category": 1,   # pk=1 NOT in fixture above (99 is)
                "name": "Ghost Product",
                "slug": "ghost-product",
                "description": "",
                "price": "1.00",
                "stock": 0,
                "is_active": True,
                "order": 0,
                "specifications": {},
            },
            category_map,
        )
    assert not Product.objects.filter(slug="ghost-product").exists()


def test_handle_import_success(tmp_path, settings):
    """Verify that handle_import runs successfully through call_command."""
    cat_fixture = _write_category_fixture(tmp_path, 1, "Category", "cat")
    prod_fixture = tmp_path / "products.json"
    prod_fixture.write_text(
        json.dumps([
            {
                "model": "products.product",
                "pk": 1,
                "fields": {
                    "category": 1,
                    "name": "Prod 1",
                    "slug": "prod-1",
                    "description": "Desc",
                    "price": "10.00",
                    "stock": 10,
                    "is_active": True,
                    "order": 1,
                    "specifications": {},
                },
            }
        ]),
        encoding="utf-8",
    )

    # Pre-create category in DB so the service can resolve it
    Category.objects.create(name="Category", slug="cat")

    # Instantiate command to override methods
    command = Command()
    command.get_fixture_paths = lambda: [prod_fixture]
    command.get_category_fixture_path = lambda: cat_fixture

    # Since we can't easily pass a pre-instantiated command object to call_command
    # and have it keep the lambda overrides, we'll manually call handle_import
    # to test the loop logic.
    result = command.handle_import()

    assert result is True
    assert Product.objects.filter(slug="prod-1").exists()
    product = Product.objects.get(slug="prod-1")
    assert product.category.slug == "cat"
