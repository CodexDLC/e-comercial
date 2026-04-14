import json

import pytest

from features.products.models import Category, Product
from system.management.commands.update_products import Command


@pytest.mark.django_db
@pytest.mark.integration
def test_upsert_product_resolves_category_from_fixture_slug(tmp_path):
    fixture_path = tmp_path / "categories.json"
    fixture_path.write_text(
        json.dumps(
            [
                {
                    "model": "products.category",
                    "pk": 1,
                    "fields": {
                        "name": "Hops",
                        "slug": "hops",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    category = Category.objects.create(name="Stored hops", slug="hops")
    from features.products.services.import_catalog import CatalogImportService
    
    command = Command()
    command.get_category_fixture_path = lambda: fixture_path

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
        },
        CatalogImportService.build_category_map([
            {
                "model": "products.category",
                "pk": 1,
                "fields": {
                    "name": "Hops",
                    "slug": "hops",
                },
            }
        ]),
    )

    product = Product.objects.get(slug="citra-hops")
    assert created is True
    assert updated is False
    assert product.category == category
