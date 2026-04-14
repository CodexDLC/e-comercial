import pytest
from django.urls import reverse
from features.reviews.models import Review

pytestmark = [pytest.mark.django_db, pytest.mark.unit]

def test_review_requires_auth(client, product):
    response = client.post(reverse('reviews:add', kwargs={'product_id': product.id}), {
        'rating': 5, 'comment': 'Great!'
    })
    assert response.status_code in (302, 403)

def test_review_created_by_auth_user(auth_client, product):
    response = auth_client.post(reverse('reviews:add', kwargs={'product_id': product.id}), {
        'rating': 4, 'comment': 'Good product'
    })
    assert response.status_code in (200, 201, 302)
    assert Review.objects.filter(product=product).exists()
