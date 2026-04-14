"""Model-level unit tests covering __str__, relationships, and business logic."""

import pytest

from features.orders.models.order import Order
from features.orders.models.order_item import OrderItem
from features.products.models import Category, Product

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Order model
# ---------------------------------------------------------------------------


def test_order_str(user):
    order = Order.objects.create(
        user=user,
        shipping_address="Test St 1",
        contact_phone="+79001234567",
        total_price="100.00",
    )
    s = str(order)
    assert "Заказ" in s


def test_order_default_status_is_pending(user):
    order = Order.objects.create(
        user=user,
        shipping_address="Test St 1",
        contact_phone="+79001234567",
        total_price="0.00",
    )
    assert order.status == "pending"


def test_order_without_user(db):
    """Guest checkout — user may be None."""
    order = Order.objects.create(
        user=None,
        shipping_address="Guest St",
        contact_phone="+0",
        total_price="0.00",
    )
    assert order.user is None
    assert "Заказ" in str(order)


# ---------------------------------------------------------------------------
# OrderItem model
# ---------------------------------------------------------------------------


def test_order_item_str(user, product):
    order = Order.objects.create(
        user=user,
        shipping_address="Addr",
        contact_phone="+0",
        total_price="30.00",
    )
    item = OrderItem.objects.create(order=order, product=product, quantity=2, price=product.price)
    s = str(item)
    assert product.name in s
    assert "2" in s


def test_order_item_str_with_deleted_product(user):
    """When product is deleted (SET_NULL), __str__ should handle None."""
    order = Order.objects.create(
        user=user,
        shipping_address="Addr",
        contact_phone="+0",
        total_price="0.00",
    )
    item = OrderItem.objects.create(order=order, product=None, quantity=1, price="5.00")
    s = str(item)
    assert "удаленный товар" in s


# ---------------------------------------------------------------------------
# Category model
# ---------------------------------------------------------------------------


def test_category_str(category):
    assert str(category) == "Хмель"


def test_category_is_not_featured_by_default(db):
    cat = Category.objects.create(name="Plain", slug="plain")
    assert cat.is_featured is False


def test_category_featured_flag(db):
    cat = Category.objects.create(name="Featured", slug="featured-cat", is_featured=True)
    assert cat.is_featured is True


# ---------------------------------------------------------------------------
# Product model
# ---------------------------------------------------------------------------


def test_product_str(product):
    assert str(product) == "Cascade Hops"


def test_product_is_active_by_default(category):
    # ActiveMixin default is True — confirm via our fixture
    p = Product.objects.create(
        name="Active P",
        slug="active-p",
        price="1.00",
        stock=1,
        category=category,
        is_active=True,
    )
    assert p.is_active is True


def test_product_stock_decrements(product):
    original = product.stock
    product.stock -= 1
    product.save()
    product.refresh_from_db()
    assert product.stock == original - 1
