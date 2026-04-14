import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def test_login_ok(client, user):
    response = client.post(reverse('account_login'), {
        'login': 'testuser', 'password': 'testpass123'
    })
    assert response.status_code in (200, 302)


def test_register_ok(client):
    response = client.post(
        f"{reverse('account_login')}?action=register",
        {
            'username': 'newuser',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        },
    )
    assert response.status_code == 302
    assert get_user_model().objects.filter(username='newuser').exists()


def test_logout(auth_client):
    response = auth_client.post(reverse('account_logout'))
    assert response.status_code in (200, 302)
