"""Unit tests for product catalog views and ProductService."""

from decimal import Decimal

import pytest
from django.urls import reverse

from features.products.models import Category, Product
from features.products.services.product import ProductService

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Catalog view — basic
# ---------------------------------------------------------------------------


def test_catalog_page_ok(client, product):
    response = client.get(reverse("products:list"))
    assert response.status_code == 200


def test_product_detail_ok(client, product):
    response = client.get(reverse("products:detail", kwargs={"slug": product.slug}))
    assert response.status_code == 200
    assert product.name in response.content.decode()


def test_product_detail_not_found(client):
    response = client.get(reverse("products:detail", kwargs={"slug": "does-not-exist"}))
    assert response.status_code == 404


def test_catalog_shows_active_products_only(client, category):
    active = Product.objects.create(
        name="Active",
        slug="active-product",
        price="10.00",
        stock=5,
        category=category,
        is_active=True,
    )
    inactive = Product.objects.create(
        name="Inactive",
        slug="inactive-product",
        price="10.00",
        stock=5,
        category=category,
        is_active=False,
    )
    response = client.get(reverse("products:list"))
    content = response.content.decode()
    assert active.name in content
    assert inactive.name not in content


def test_catalog_empty(client, category):
    """Catalog page should render even with no products."""
    response = client.get(reverse("products:list"))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Catalog view — search / filter / sort
# ---------------------------------------------------------------------------


def test_catalog_search_by_name(client, category):
    p = Product.objects.create(
        name="Unique Citra",
        slug="unique-citra",
        price="9.00",
        stock=10,
        category=category,
        is_active=True,
    )
    response = client.get(reverse("products:list"), {"q": "Unique Citra"})
    assert response.status_code == 200
    assert p.name in response.content.decode()


def test_catalog_search_excludes_non_matching(client, category):
    Product.objects.create(
        name="Galaxy Hops",
        slug="galaxy-hops",
        price="8.00",
        stock=5,
        category=category,
        is_active=True,
    )
    response = client.get(reverse("products:list"), {"q": "ZZZ_nomatch_ZZZ"})
    assert response.status_code == 200
    assert "Galaxy Hops" not in response.content.decode()


def test_catalog_filter_by_category(client, category):
    other_cat = Category.objects.create(name="Yeast", slug="yeast")
    p_in = Product.objects.create(
        name="Ale Yeast",
        slug="ale-yeast",
        price="5.00",
        stock=20,
        category=other_cat,
        is_active=True,
    )
    response = client.get(reverse("products:list"), {"category": "yeast"})
    assert response.status_code == 200
    assert p_in.name in response.content.decode()


def test_catalog_sort_price_asc(client, category):
    response = client.get(reverse("products:list"), {"sort": "price_asc"})
    assert response.status_code == 200


def test_catalog_sort_price_desc(client, category):
    response = client.get(reverse("products:list"), {"sort": "price_desc"})
    assert response.status_code == 200


def test_catalog_sort_rating(client, category):
    response = client.get(reverse("products:list"), {"sort": "rating"})
    assert response.status_code == 200


def test_product_detail_authenticated_has_review_context(auth_client, product, user):
    """Authenticated user should get has_review in context."""
    response = auth_client.get(reverse("products:detail", kwargs={"slug": product.slug}))
    assert response.status_code == 200
    assert "has_review" in response.context


def test_product_detail_anonymous_has_no_review(client, product):
    """Anonymous user has_review must be False."""
    response = client.get(reverse("products:detail", kwargs={"slug": product.slug}))
    assert response.status_code == 200
    assert response.context["has_review"] is False


# ---------------------------------------------------------------------------
# ProductService unit tests
# ---------------------------------------------------------------------------


def test_product_service_update_stock(product):
    ProductService.update_stock(product.id, 42)
    product.refresh_from_db()
    assert product.stock == 42


def test_product_service_toggle_active_deactivates(product):
    assert product.is_active is True
    result = ProductService.toggle_active_status(product.id)
    assert result is False
    product.refresh_from_db()
    assert product.is_active is False


def test_product_service_toggle_active_reactivates(product):
    product.is_active = False
    product.save()
    result = ProductService.toggle_active_status(product.id)
    assert result is True
    product.refresh_from_db()
    assert product.is_active is True


# ---------------------------------------------------------------------------
# Model unit tests (no HTTP)
# ---------------------------------------------------------------------------


def test_product_str(product):
    assert str(product) == product.name


def test_category_str(category):
    assert str(category) == category.name


def test_product_default_stock_is_zero(category):
    p = Product(
        name="No Stock",
        slug="no-stock",
        price="5.00",
        category=category,
        is_active=True,
    )
    assert p.stock == 0


def test_category_parent_relationship(category):
    child = Category.objects.create(name="Child Cat", slug="child-cat", parent=category)
    assert child.parent == category
    assert child in list(category.children.all())


def test_product_price_is_decimal(product):
    product.refresh_from_db()
    assert isinstance(product.price, Decimal)
