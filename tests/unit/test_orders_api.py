import pytest
from django.urls import reverse
from rest_framework import status
from features.orders.models.order import Order
from features.orders.models.order_item import OrderItem

@pytest.mark.django_db
class TestOrdersAPI:
    def test_list_orders_unauthenticated(self, client):
        url = reverse("order-list")
        response = client.get(url)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_list_orders_authenticated(self, auth_client, user):
        url = reverse("order-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_order_empty_cart(self, auth_client):
        url = reverse("order-list")
        response = auth_client.post(url, {"shipping_address": "Test Addr", "contact_phone": "123"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Корзина пуста" in response.data["detail"]

    def test_create_order_with_items(self, auth_client, product):
        # Add to cart first (using session-based cart via API)
        auth_client.post(reverse("cart-add"), {"product_id": product.id, "quantity": 2})
        
        url = reverse("order-list")
        data = {
            "shipping_address": "123 Main St",
            "contact_phone": "+123456789"
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        order = Order.objects.get(id=response.data["id"])
        assert order.shipping_address == "123 Main St"
        from decimal import Decimal
        assert order.total_price == Decimal(product.price) * 2
        assert OrderItem.objects.filter(order=order).count() == 1

@pytest.mark.django_db
class TestCartAPI:
    def test_cart_operations(self, client, product):
        # List empty
        response = client.get(reverse("cart-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {}
        
        # Add item
        response = client.post(reverse("cart-add"), {"product_id": product.id, "quantity": 3})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {str(product.id): 3}
        
        # Remove item
        response = client.post(reverse("cart-remove"), {"product_id": product.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {}
