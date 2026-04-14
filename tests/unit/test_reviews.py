"""Unit tests for product reviews."""

import pytest
from django.urls import reverse

from features.reviews.models import Review

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def test_review_requires_auth(client, product):
    response = client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        {"rating": 5, "comment": "Great!"},
    )
    assert response.status_code in (302, 403)


def test_review_created_by_auth_user(auth_client, product):
    response = auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        {"rating": 4, "comment": "Good product"},
    )
    assert response.status_code in (200, 201, 302)
    assert Review.objects.filter(product=product).exists()


def test_review_requires_comment(auth_client, product):
    """Empty comment should not create a review."""
    auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        {"rating": 3, "comment": ""},
    )
    assert not Review.objects.filter(product=product, comment="").exists()


def test_review_requires_rating(auth_client, product):
    """Missing rating should not create a review."""
    auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        {"comment": "Good"},
    )
    assert not Review.objects.filter(product=product, comment="Good").exists()


def test_duplicate_review_rejected(auth_client, product, user):
    """Second review by same user on same product should be rejected."""
    payload = {"rating": 5, "comment": "First review"}
    auth_client.post(reverse("reviews:add", kwargs={"product_id": product.id}), payload)
    auth_client.post(reverse("reviews:add", kwargs={"product_id": product.id}), payload)
    assert Review.objects.filter(product=product, user=user).count() == 1


def test_review_str(product, user):
    review = Review.objects.create(product=product, user=user, rating=5, comment="Nice")
    expected = f"Отзыв на {product.name} от {user.username}"
    assert str(review) == expected


def test_review_for_inactive_product_returns_404(auth_client, category):
    from features.products.models import Product

    inactive = Product.objects.create(
        name="Inactive P",
        slug="inactive-p",
        price="1.00",
        stock=10,
        category=category,
        is_active=False,
    )
    response = auth_client.post(
        reverse("reviews:add", kwargs={"product_id": inactive.id}),
        {"rating": 3, "comment": "Hmm"},
    )
    assert response.status_code == 404


def test_review_htmx_returns_html_fragment(auth_client, product):
    """HTMX request should return an HTML fragment (200) not a redirect."""
    response = auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        {"rating": 5, "comment": "Great via HTMX"},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert Review.objects.filter(product=product).exists()


def test_review_htmx_duplicate_returns_409(auth_client, product, user):
    """Duplicate HTMX review should return 409 Conflict."""
    payload = {"rating": 5, "comment": "First"}
    auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        payload,
        HTTP_HX_REQUEST="true",
    )
    response = auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        payload,
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 409


def test_review_htmx_missing_fields_returns_400(auth_client, product):
    """HTMX request with missing rating/comment should return 400."""
    response = auth_client.post(
        reverse("reviews:add", kwargs={"product_id": product.id}),
        {"rating": "", "comment": ""},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 400
