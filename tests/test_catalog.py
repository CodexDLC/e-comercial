import pytest
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.unit]

def test_catalog_page_ok(client, product):
    response = client.get(reverse('products:list'))
    assert response.status_code == 200

def test_product_detail_ok(client, product):
    response = client.get(reverse('products:detail', kwargs={'slug': product.slug}))
    assert response.status_code == 200
    assert product.name in response.content.decode()
