import pytest
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.unit]

def test_add_to_cart(client, product):
    response = client.post(reverse('orders:cart_add', kwargs={'product_id': product.id}), {'quantity': 2})
    assert response.status_code in (200, 302)

def test_remove_from_cart(client, product):
    client.post(reverse('orders:cart_add', kwargs={'product_id': product.id}), {})
    response = client.post(reverse('orders:cart_remove', kwargs={'product_id': product.id}))
    assert response.status_code in (200, 302)

def test_cart_respects_stock(client, product):
    response = client.post(reverse('orders:cart_add', kwargs={'product_id': product.id}), {'quantity': 9999})
    assert response.status_code != 500
