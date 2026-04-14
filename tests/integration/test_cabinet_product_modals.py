from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from features.products.models import Category, Product


class ProductModalFlowTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.staff_user = user_model.objects.create_user(
            username="manager",
            email="manager@example.com",
            is_staff=True,
        )
        self.category = Category.objects.create(name="Malt", slug="malt")
        self.product = Product.objects.create(
            name="Pilsner Malt",
            slug="pilsner-malt",
            category=self.category,
            price=Decimal("20.00"),
            stock=5,
            is_active=True,
        )

    def test_product_create_modal_get_returns_modal_form(self) -> None:
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("cabinet:product_create"), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Product")
        self.assertContains(response, 'hx-target="#cabinet-modal-content"', html=False)

    def test_product_create_modal_invalid_post_renders_errors(self) -> None:
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("cabinet:product_create"),
            {"name": "", "category": ""},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertEqual(Product.objects.count(), 1)

    def test_product_create_modal_valid_htmx_post_returns_trigger(self) -> None:
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("cabinet:product_create"),
            {
                "name": "Vienna Malt",
                "category": self.category.pk,
                "description": "Fresh malt",
                "price": "22.50",
                "stock": "11",
                "is_active": "on",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["HX-Trigger"], "products-updated")
        self.assertTrue(Product.objects.filter(name="Vienna Malt").exists())

    def test_product_update_modal_get_returns_edit_form(self) -> None:
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("cabinet:product_update", args=[self.product.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Product")
        self.assertContains(response, self.product.name)
