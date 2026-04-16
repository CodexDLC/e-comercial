from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from features.conversations.models import Message
from features.orders.models import Order, OrderItem
from features.products.models import Category, Product


class AnalyticsReportsTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.staff_user = user_model.objects.create_user(
            username="staff",
            email="staff@example.com",
            is_staff=True,
        )
        self.customer = user_model.objects.create_user(
            username="customer",
            email="customer@example.com",
        )
        self.category = Category.objects.create(name="Hops", slug="hops")
        self.product = Product.objects.create(
            name="Cascade Hops",
            slug="cascade-hops",
            category=self.category,
            price=Decimal("15.00"),
            stock=24,
            is_active=True,
        )

        first_order = Order.objects.create(
            user=self.customer,
            status="delivered",
            total_price=Decimal("120.00"),
            shipping_address="Main street 1",
            contact_phone="+49123456",
        )
        second_order = Order.objects.create(
            user=self.customer,
            status="processing",
            total_price=Decimal("80.00"),
            shipping_address="Main street 1",
            contact_phone="+49123456",
        )
        OrderItem.objects.create(order=first_order, product=self.product, quantity=3, price=Decimal("15.00"))
        OrderItem.objects.create(order=second_order, product=self.product, quantity=2, price=Decimal("17.50"))
        Message.objects.create(
            sender_name="Buyer",
            sender_email="buyer@example.com",
            body="Where is my order?",
            status=Message.Status.OPEN,
        )

    def test_reports_page_uses_real_revenue_data(self) -> None:
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("cabinet:analytics_reports"), {"tab": "revenue", "period": "month"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revenue")
        self.assertContains(response, "$200.00")
        self.assertContains(response, "Average Order")
        self.assertNotContains(response, "Mocked analytics summary")
        self.assertNotContains(response, "All team")
        self.assertNotContains(response, "Elena S.")
        self.assertEqual(response.context["active_tab"], "revenue")
        self.assertEqual(response.context["summary_row"]["orders"], 2)
        self.assertEqual(response.context["summary_row"]["revenue_fmt"], "$200.00")

    def test_reports_page_builds_product_and_customer_tabs_from_live_models(self) -> None:
        self.client.force_login(self.staff_user)

        products_response = self.client.get(
            reverse("cabinet:analytics_reports"),
            {"tab": "products", "period": "month"},
        )
        customers_response = self.client.get(
            reverse("cabinet:analytics_reports"),
            {"tab": "customers", "period": "month"},
        )

        self.assertEqual(products_response.status_code, 200)
        self.assertContains(products_response, "Cascade Hops")
        self.assertContains(products_response, "Units")
        self.assertContains(products_response, "$80.00")
        self.assertNotContains(products_response, "Bookings")

        self.assertEqual(customers_response.status_code, 200)
        self.assertContains(customers_response, "New Users")
        self.assertContains(customers_response, "Messages")
        self.assertNotContains(customers_response, "Units")
        self.assertContains(customers_response, "Customer Activity")
        self.assertEqual(customers_response.context["summary_cards"][0]["value"], "2")

    def test_reports_context_period_label_matches_current_date_window(self) -> None:
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("cabinet:analytics_reports"), {"tab": "revenue", "period": "week"})

        self.assertEqual(response.status_code, 200)
        today = timezone.now().date()
        expected_start = (today - timedelta(days=6)).strftime("%d.%m.%Y")
        expected_end = today.strftime("%d.%m.%Y")
        self.assertIn(expected_start, response.context["period_label"])
        self.assertIn(expected_end, response.context["period_label"])
