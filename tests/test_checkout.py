import pytest
from django.urls import reverse
from features.orders.models import Order

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

def test_checkout_creates_order(auth_client, product, user):
    auth_client.post(reverse('orders:cart_add', kwargs={'product_id': product.id}), {'quantity': 1})
    
    initial_stock = product.stock
    response = auth_client.post(reverse('orders:checkout'), {
        'full_name': 'Test User',
        'email': 'test@test.com',
        'phone': '+70000000000',
        'address': 'Test Address 1',
    })
    assert response.status_code in (200, 302)
    
    assert Order.objects.filter(user=user).exists()
    
    product.refresh_from_db()
    assert product.stock == initial_stock - 1
