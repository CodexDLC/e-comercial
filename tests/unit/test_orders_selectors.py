import pytest
from features.orders.models.order import Order
from features.orders.selectors.order import OrderSelector

@pytest.fixture
def order_factory(db, user):
    def _create(**kwargs):
        defaults = {
            "user": user,
            "shipping_address": "Test Addr",
            "contact_phone": "123",
            "total_price": 100,
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)
    return _create

@pytest.mark.django_db
class TestOrderSelectors:
    def test_get_orders_list(self, order_factory, user):
        o1 = order_factory(status="pending")
        o2 = order_factory(status="completed")
        
        qs = OrderSelector.get_orders_list()
        assert qs.count() == 2
        
        qs_filtered = OrderSelector.get_orders_list(status_filter="pending")
        assert qs_filtered.count() == 1
        assert o1 in qs_filtered
