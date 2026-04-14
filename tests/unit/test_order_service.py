from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from features.orders.models.order import Order
from features.orders.models.order_item import OrderItem
from features.orders.services.order import OrderService


@pytest.mark.django_db
@pytest.mark.unit
class TestOrderService:
    def test_create_order_workflow(self, user, product):
        # Mock Cart
        cart = MagicMock()
        cart.get_total_price.return_value = Decimal("100.00")
        cart.__iter__.return_value = [
            {
                "product": product,
                "price": Decimal("100.00"),
                "quantity": 1,
            }
        ]

        initial_stock = product.stock

        order = OrderService.create_order(
            user=user,
            cart=cart,
            full_name="Testing User",
            email="test@example.com",
            phone="+70000000000",
            address="Test Address",
        )

        # Verify Order creation
        assert Order.objects.count() == 1
        assert order.total_price == Decimal("100.00")
        assert order.contact_phone == "+70000000000"

        # Verify OrderItem creation
        assert OrderItem.objects.count() == 1
        item = OrderItem.objects.first()
        assert item.order == order
        assert item.product == product

        # Verify Stock update
        product.refresh_from_db()
        assert product.stock == initial_stock - 1

        # Verify Cart clear call
        cart.clear.assert_called_once()
