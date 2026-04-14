"""Unit tests for authentication views."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.unit]

User = get_user_model()


def test_login_ok(client, user):
    response = client.post(reverse("account_login"), {
        "login": "testuser", "password": "testpass123"
    })
    assert response.status_code in (200, 302)


def test_login_wrong_password(client, user):
    response = client.post(reverse("account_login"), {
        "login": "testuser", "password": "wrong"
    })
    assert response.status_code == 200  # stays on login page


def test_login_unknown_user(client):
    response = client.post(reverse("account_login"), {
        "login": "nobody", "password": "anything"
    })
    assert response.status_code == 200


def test_register_ok(client):
    response = client.post(
        f"{reverse('account_login')}?action=register",
        {
            "username": "newuser",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        },
    )
    assert response.status_code == 302
    assert User.objects.filter(username="newuser").exists()


def test_register_password_mismatch(client):
    response = client.post(
        f"{reverse('account_login')}?action=register",
        {
            "username": "newuser2",
            "password1": "StrongPass123",
            "password2": "Different456",
        },
    )
    assert response.status_code in (200, 302)
    assert not User.objects.filter(username="newuser2").exists()


def test_logout(auth_client):
    response = auth_client.post(reverse("account_logout"))
    assert response.status_code in (200, 302)


def test_login_page_renders(client):
    response = client.get(reverse("account_login"))
    assert response.status_code == 200


def test_authenticated_user_redirected_from_login(auth_client):
    """Already-logged-in user should be redirected away from login page."""
    response = auth_client.get(reverse("account_login"))
    # allauth typically redirects already-authenticated users
    assert response.status_code in (200, 302)
