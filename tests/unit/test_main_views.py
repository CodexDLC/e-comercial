"""Unit tests for main app views (home, contacts, guides, community, resources)."""

import pytest
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def test_home_page_renders(client):
    response = client.get(reverse("main:home"))
    assert response.status_code == 200


def test_home_page_shows_active_products(client, product):
    response = client.get(reverse("main:home"))
    assert response.status_code == 200
    assert product.name in response.content.decode()


def test_home_page_search(client, product):
    response = client.get(reverse("main:home"), {"q": product.name})
    assert response.status_code == 200


def test_home_page_sort_price_asc(client):
    response = client.get(reverse("main:home"), {"sort": "price_asc"})
    assert response.status_code == 200


def test_home_page_sort_price_desc(client):
    response = client.get(reverse("main:home"), {"sort": "price_desc"})
    assert response.status_code == 200


def test_home_page_sort_rating(client):
    response = client.get(reverse("main:home"), {"sort": "rating"})
    assert response.status_code == 200


def test_home_page_category_filter(client, category):
    response = client.get(reverse("main:home"), {"category": category.slug})
    assert response.status_code == 200


def test_contacts_page_renders(client):
    response = client.get(reverse("main:contacts"))
    assert response.status_code == 200


def test_contacts_page_has_form(client):
    response = client.get(reverse("main:contacts"))
    assert "form" in response.context


def test_contacts_post_valid_creates_message(client):
    from features.conversations.models import Message

    before = Message.objects.count()
    response = client.post(
        reverse("main:contacts"),
        {
            "sender_name": "Test User",
            "sender_email": "test@example.com",
            "sender_phone": "",
            "subject": "Hello",
            "topic": "other",
            "body": "I have a question about your products.",
        },
    )
    assert response.status_code in (200, 302)
    assert Message.objects.count() == before + 1


def test_contacts_post_invalid_stays_on_page(client):
    from features.conversations.models import Message

    before = Message.objects.count()
    response = client.post(
        reverse("main:contacts"),
        {"sender_name": "", "sender_email": "not-an-email", "body": ""},
    )
    assert response.status_code == 200
    assert Message.objects.count() == before


def test_guides_page_renders(client):
    response = client.get(reverse("main:guides-recipes"))
    assert response.status_code == 200


def test_community_page_renders(client):
    response = client.get(reverse("main:community"))
    assert response.status_code == 200


def test_resources_page_renders(client):
    response = client.get(reverse("main:resources"))
    assert response.status_code == 200
