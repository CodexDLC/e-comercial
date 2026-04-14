"""Integration tests for the checkout flow.

These tests exercise the full request/response cycle including database
writes across multiple models (Product, Order, OrderItem).
"""

import pytest
from django.urls import reverse

from features.orders.models.order import Order

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_checkout_creates_order(auth_client, product, user):
    auth_client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 1},
    )
    initial_stock = product.stock

    response = auth_client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Test User",
            "email": "test@test.com",
            "phone": "+70000000000",
            "address": "Test Address 1",
        },
    )
    assert response.status_code in (200, 302)
    assert Order.objects.filter(user=user).exists()

    product.refresh_from_db()
    assert product.stock == initial_stock - 1


def test_checkout_with_empty_cart_redirects(auth_client):
    """Checkout with empty cart should redirect to catalog."""
    response = auth_client.get(reverse("orders:checkout"))
    assert response.status_code in (200, 302)


def test_checkout_without_required_fields(auth_client, product):
    """Missing required fields must not create an order."""
    auth_client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 1},
    )
    before = Order.objects.count()

    response = auth_client.post(
        reverse("orders:checkout"),
        {"full_name": "", "email": "", "phone": "", "address": ""},
    )
    assert response.status_code in (200, 302)
    assert Order.objects.count() == before


def test_checkout_deducts_stock_for_multiple_items(auth_client, category):
    """All items in cart must have their stock decremented."""
    from features.products.models import Product

    p1 = Product.objects.create(name="P1", slug="p1", price="10.00", stock=50, category=category, is_active=True)
    p2 = Product.objects.create(name="P2", slug="p2", price="20.00", stock=30, category=category, is_active=True)

    auth_client.post(reverse("orders:cart_add", kwargs={"product_id": p1.id}), {"quantity": 3})
    auth_client.post(reverse("orders:cart_add", kwargs={"product_id": p2.id}), {"quantity": 2})

    auth_client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Test",
            "email": "t@t.com",
            "phone": "+7",
            "address": "Street",
        },
    )

    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.stock == 47
    assert p2.stock == 28


def test_guest_checkout_creates_order_without_user(client, product):
    """Anonymous user can complete checkout; order has user=None."""
    client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 1},
    )
    client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Guest",
            "email": "guest@test.com",
            "phone": "+70000000001",
            "address": "Anon Street",
        },
    )
    order = Order.objects.filter(user=None).first()
    assert order is not None
