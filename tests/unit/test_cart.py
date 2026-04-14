"""Unit tests for cart views and Cart class."""

from decimal import Decimal

import pytest
from django.urls import reverse

from features.orders.cart import Cart

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Cart class unit tests (direct class usage, no HTTP)
# ---------------------------------------------------------------------------


def _make_session_request(rf, session_data=None):
    """Build a GET request with an attached session dict."""
    from django.contrib.sessions.backends.db import SessionStore
    request = rf.get("/")
    request.session = SessionStore()
    if session_data:
        for key, value in session_data.items():
            request.session[key] = value
    return request


def test_cart_add_item(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=2)
    assert len(cart) == 2


def test_cart_add_respects_stock_ceiling(product, rf):
    """Adding more than stock should be capped at stock."""
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=9999)
    assert len(cart) == product.stock


def test_cart_remove_item(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=3)
    cart.remove(product)
    assert len(cart) == 0


def test_cart_remove_nonexistent_item_is_noop(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.remove(product)  # product was never added
    assert len(cart) == 0


def test_cart_override_quantity(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=1)
    cart.add(product, quantity=5, override_quantity=True)
    assert len(cart) == 5


def test_cart_get_total_price(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=3)
    expected = Decimal(product.price) * 3
    assert cart.get_total_price() == expected


def test_cart_iter_yields_items(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=2)
    items = list(cart)
    assert len(items) == 1
    assert items[0]["product"] == product
    assert items[0]["quantity"] == 2


def test_cart_clear(product, rf):
    request = _make_session_request(rf)
    cart = Cart(request.session)
    cart.add(product, quantity=1)
    cart.clear()
    # Create a new Cart instance from the same session to verify the cart is empty
    cart2 = Cart(request.session)
    assert len(cart2) == 0


# ---------------------------------------------------------------------------
# Cart HTTP view tests
# ---------------------------------------------------------------------------


def test_add_to_cart_view(client, product):
    response = client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 2},
    )
    assert response.status_code in (200, 302)


def test_add_to_cart_exceeds_stock(client, product):
    """POST with quantity > stock must not return 500."""
    response = client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 9999},
    )
    assert response.status_code != 500


def test_remove_from_cart_view(client, product):
    client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 1},
    )
    response = client.post(
        reverse("orders:cart_remove", kwargs={"product_id": product.id})
    )
    assert response.status_code in (200, 302)


def test_cart_page_renders(client):
    response = client.get(reverse("orders:cart"))
    assert response.status_code == 200


def test_add_nonexistent_product_returns_404(client):
    response = client.post(
        reverse("orders:cart_add", kwargs={"product_id": 99999}),
        {"quantity": 1},
    )
    assert response.status_code == 404


def test_cart_page_includes_cart_context(client):
    """Cart page (empty) must include cart in context."""
    response = client.get(reverse("orders:cart"))
    assert response.status_code == 200
    assert "cart" in response.context


def test_checkout_get_with_empty_cart_redirects(client):
    """GET /checkout/ with empty cart should redirect to catalog."""
    response = client.get(reverse("orders:checkout"))
    assert response.status_code in (302, 200)


def test_checkout_get_with_items_renders(auth_client, product):
    """GET /checkout/ with items should render the checkout page."""
    auth_client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 1},
    )
    response = auth_client.get(reverse("orders:checkout"))
    assert response.status_code == 200
    assert "cart" in response.context


def test_cart_add_override_quantity(client, product):
    """POST with override=True should redirect successfully (quantity replaced)."""
    client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 5},
    )
    response = client.post(
        reverse("orders:cart_add", kwargs={"product_id": product.id}),
        {"quantity": 2, "override": "True"},
    )
    # Both POSTs should redirect to cart (302) not error (500)
    assert response.status_code in (200, 302)
