from decimal import Decimal

import pytest
from django.urls import reverse

from features.orders.models import Order, OrderItem


@pytest.mark.unit
@pytest.mark.django_db
class TestOrdersViews:
    def test_cart_add_view(self, client, product):
        url = reverse("orders:cart_add", kwargs={"product_id": product.id})
        response = client.post(url, {"quantity": 2})
        assert response.status_code == 302  # Redirects to cart

        # Check session
        cart = client.session.get("cart", {})
        assert str(product.id) in cart
        assert cart[str(product.id)]["quantity"] == 2

    def test_cart_remove_view(self, client, product):
        # Add first
        s = client.session
        s["cart"] = {str(product.id): {"quantity": 5, "price": str(product.price)}}
        s.save()

        url = reverse("orders:cart_remove", kwargs={"product_id": product.id})
        response = client.post(url)
        assert response.status_code == 302
        assert str(product.id) not in client.session.get("cart", {})

    def test_checkout_get_empty_cart(self, client):
        url = reverse("orders:checkout")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse("products:list")

    def test_checkout_post_success(self, client, product, user):
        # Add item to cart
        s = client.session
        s["cart"] = {str(product.id): {"quantity": 1, "price": str(product.price)}}
        s.save()

        client.force_login(user)
        url = reverse("orders:checkout")
        data = {"full_name": "Test User", "email": "test@example.com", "phone": "123456789", "address": "Test Street 1"}
        response = client.post(url, data)
        assert response.status_code == 302

        # Verify order created
        order = Order.objects.first()
        assert order is not None
        assert order.user == user
        assert order.total_price == Decimal(str(product.price))
        assert OrderItem.objects.filter(order=order).count() == 1

        # Verify stock update
        product.refresh_from_db()
        assert product.stock == 99  # Assuming initial was 100

    def test_checkout_post_missing_fields(self, client, product):
        # Add item to cart
        s = client.session
        s["cart"] = {str(product.id): {"quantity": 1, "price": str(product.price)}}
        s.save()

        url = reverse("orders:checkout")
        data = {"full_name": "Test User"}  # Missing others
        response = client.post(url, data)
        assert response.status_code == 200
        assert "Пожалуйста, заполните все обязательные поля" in response.content.decode("utf-8")
