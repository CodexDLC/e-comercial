import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ROOT_URLCONF="core.urls",
)
@pytest.mark.unit
class AuthViewsTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123"
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_register_page_renders(self):
        response = self.client.get(f"{reverse('account_login')}?action=register")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")

    def test_register_creates_user_and_redirects(self):
        response = self.client.post(
            f"{reverse('account_login')}?action=register",
            {
                "username": "newuser",
                "password1": "NewStrongPass123",
                "password2": "NewStrongPass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get("_auth_user_id"))
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())

    def test_logout_confirmation_page_renders_on_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_logout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/logout.html")

    def test_logout_post_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("account_logout"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].endswith("/cabinet/login/"))

    def test_password_reset_request_page_renders(self):
        response = self.client.get(reverse("account_reset_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/password_reset.html")

    def test_password_reset_request_sends_email(self):
        response = self.client.post(
            reverse("account_reset_password"),
            {"email": self.user.email},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/password/reset/key/", mail.outbox[0].body)
