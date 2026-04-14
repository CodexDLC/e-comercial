import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from features.orders.services.cart import CartService


@pytest.fixture
def request_with_session(rf):
    request = rf.get("/")
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request


class TestCartService:
    def test_get_cart_empty(self, request_with_session):
        cart = CartService.get_cart(request_with_session)
        assert cart == {}

    def test_add_item(self, request_with_session):
        CartService.add(request_with_session, product_id=1, quantity=2)
        cart = CartService.get_cart(request_with_session)
        assert cart == {"1": 2}

        CartService.add(request_with_session, product_id=1, quantity=3)
        cart = CartService.get_cart(request_with_session)
        assert cart == {"1": 5}

    def test_add_different_items(self, request_with_session):
        CartService.add(request_with_session, product_id=1)
        CartService.add(request_with_session, product_id="2", quantity=2)
        cart = CartService.get_cart(request_with_session)
        assert cart == {"1": 1, "2": 2}

    def test_remove_item(self, request_with_session):
        CartService.add(request_with_session, product_id=1)
        CartService.remove(request_with_session, product_id=1)
        cart = CartService.get_cart(request_with_session)
        assert cart == {}

    def test_remove_non_existent(self, request_with_session):
        CartService.remove(request_with_session, product_id=999)
        cart = CartService.get_cart(request_with_session)
        assert cart == {}

    def test_clear_cart(self, request_with_session):
        CartService.add(request_with_session, product_id=1)
        CartService.clear(request_with_session)
        cart = CartService.get_cart(request_with_session)
        assert cart == {}
