import pytest
from django.urls import reverse
from rest_framework import status

from features.reviews.models.review import Review


@pytest.mark.django_db
class TestReviewsAPI:
    def test_list_reviews(self, client, product, user):
        Review.objects.create(product=product, user=user, rating=5, comment="Great!")
        url = reverse("review-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Handle potential pagination
        results = response.data.get("results", response.data)
        assert len(results) == 1

    def test_filter_reviews_by_product(self, client, product, user, category):
        p2 = product.__class__.objects.create(name="Other", slug="other", price=10, category=category)
        Review.objects.create(product=product, user=user, rating=5)
        Review.objects.create(product=p2, user=user, rating=4)

        url = reverse("review-list")
        response = client.get(url, {"product_id": product.id})
        # Handle potential pagination
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["product"] == product.id

    def test_create_review_unauthenticated(self, client, product):
        url = reverse("review-list")
        response = client.post(url, {"product": product.id, "rating": 5, "comment": "Nice"})
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_create_review_authenticated(self, auth_client, product, user):
        url = reverse("review-list")
        data = {"product": product.id, "rating": 4, "comment": "Good product"}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.filter(product=product, user=user).exists()
