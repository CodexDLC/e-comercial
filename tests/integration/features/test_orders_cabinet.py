from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from features.orders.models import Order

User = get_user_model()


class ClientOrdersCabinetTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="client",
            email="client@example.com",
            first_name="John",
            last_name="Doe",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
        )
        self.url = reverse("cabinet:client_home")

    def test_client_home_shows_only_current_user_orders(self) -> None:
        visible_order = Order.objects.create(
            user=self.user,
            status="pending",
            total_price=Decimal("123.45"),
            shipping_address="John Doe\nclient@example.com\nMain Street 1",
            contact_phone="+491234567",
        )
        Order.objects.create(
            user=self.other_user,
            status="cancelled",
            total_price=Decimal("999.99"),
            shipping_address="Hidden User\nother@example.com\nOther Street 9",
            contact_phone="+499999999",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        orders_table = response.context["orders_table"]
        self.assertEqual(response.context["orders_total_count"], 1)
        self.assertEqual(response.context["orders_visible_count"], 1)
        self.assertEqual(len(orders_table.rows), 1)
        self.assertEqual(orders_table.rows[0]["status"], "pending")
        self.assertEqual(orders_table.rows[0]["status_label"], visible_order.get_status_display())
        self.assertEqual(orders_table.rows[0]["total"], "123.45")
        self.assertIn("Main Street 1", orders_table.rows[0]["shipping_address"])
        self.assertEqual(orders_table.rows[0]["status_color_map"]["pending"], "warning")
        self.assertEqual(orders_table.rows[0]["status_color_map"]["delivered"], "success")
        self.assertEqual(orders_table.rows[0]["status_color_map"]["cancelled"], "danger")

        content = response.content.decode("utf-8")
        self.assertIn("My Orders", content)
        self.assertIn("123.45", content)
        self.assertIn("Main Street 1", content)
        self.assertIn(str(visible_order.id).split("-")[0], content)
        self.assertNotIn("Other Street 9", content)

    def test_client_home_uses_empty_orders_state_when_user_has_no_orders(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        orders_table = response.context["orders_table"]
        self.assertEqual(response.context["orders_total_count"], 0)
        self.assertEqual(response.context["orders_visible_count"], 0)
        self.assertEqual(orders_table.rows, [])
        self.assertEqual(orders_table.empty_message, "No orders yet.")

    def test_client_orders_page_uses_real_order_data_instead_of_mock_blocks(self) -> None:
        Order.objects.create(
            user=self.user,
            status="processing",
            total_price=Decimal("50.00"),
            shipping_address="Client User\nclient@example.com\nActive Street 1",
            contact_phone="+491111111",
        )
        Order.objects.create(
            user=self.user,
            status="delivered",
            total_price=Decimal("75.00"),
            shipping_address="Client User\nclient@example.com\nHistory Street 2",
            contact_phone="+492222222",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("cabinet:client_orders"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["client_page_title"], "My Orders")
        self.assertEqual(response.context["active_orders_total_count"], 1)
        self.assertEqual(response.context["history_total_count"], 1)
        self.assertEqual(len(response.context["active_orders_table"].rows), 1)
        self.assertEqual(len(response.context["history_table"].rows), 1)

        content = response.content.decode("utf-8")
        self.assertIn("My Orders", content)
        self.assertIn("Active Orders", content)
        self.assertIn("Order History", content)
        self.assertNotIn("Mock demo data", content)
        self.assertNotIn("My Appointments", content)
