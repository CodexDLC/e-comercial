from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, cast

if TYPE_CHECKING:
    from django.contrib.auth.models import User

from codex_django.cabinet import DataTableData, MetricWidgetData, TableColumn
from django.db.models import Count, Sum
from django.http import HttpRequest
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from features.orders.models import Order, OrderItem
from features.reviews.models import Review
from system.services import ClientProfileService


@dataclass(frozen=True)
class ClientSummaryCard:
    label: str
    value: str
    hint: str = ""
    icon: str = ""


@dataclass(frozen=True)
class ClientOrderRow:
    number: str
    created_at: str
    total: str
    shipping_address: str
    status: str
    status_tone: str


class ClientService:
    CLOSED_ORDER_STATUSES: ClassVar[set[str]] = {"delivered", "cancelled"}
    ORDER_STATUS_COLOR_MAP: ClassVar[dict[str, str]] = {
        "pending": "warning",
        "processing": "warning",
        "shipped": "primary",
        "delivered": "success",
        "cancelled": "danger",
    }

    @staticmethod
    def _format_order_number_cell(row: ClientOrderRow) -> str:
        return format_html(
            '<div class="fw-semibold">#{}</div><div class="text-muted small">{}</div>',
            row.number,
            row.created_at,
        )

    @classmethod
    def _build_orders_table(cls, rows: list[ClientOrderRow]) -> DataTableData:
        return DataTableData(
            columns=[
                TableColumn(key="number_date", label=str(_("Order")), bold=True),
                TableColumn(key="total", label=str(_("Total")), align="right"),
                TableColumn(key="shipping_address", label=str(_("Shipping Address"))),
                TableColumn(
                    key="status_label",
                    label=str(_("Status")),
                    badge_key="status_color_map",
                ),
            ],
            rows=[
                {
                    "number_date": cls._format_order_number_cell(row),
                    "total": row.total,
                    "shipping_address": row.shipping_address,
                    "status": row.status_tone,
                    "status_label": row.status,
                    "status_color_map": cls.ORDER_STATUS_COLOR_MAP,
                }
                for row in rows
            ],
            empty_message=str(_("No orders yet.")),
        )

    @staticmethod
    def _build_order_rows(orders: list[Order]) -> list[ClientOrderRow]:
        return [
            ClientOrderRow(
                number=str(order.id).split("-")[0],
                created_at=date_format(localtime(order.created_at), "d.m.Y H:i"),
                total=f"{order.total_price:.2f}",
                shipping_address=order.shipping_address,
                status=order.get_status_display(),
                status_tone=order.status,
            )
            for order in orders
        ]

    @classmethod
    def get_corner_context(cls, request: HttpRequest) -> dict[str, object]:
        user = cast("User", request.user)
        profile, payload = ClientProfileService.get_profile_payload(user)
        orders_queryset = Order.objects.filter(user=user).order_by("-created_at")
        orders = list(orders_queryset[:10])
        order_rows = cls._build_order_rows(orders)
        orders_total_count = orders_queryset.count()
        active_orders_count = orders_queryset.exclude(status__in=cls.CLOSED_ORDER_STATUSES).count()
        spent_total = orders_queryset.exclude(status="cancelled").aggregate(total=Sum("total_price"))[
            "total"
        ] or Decimal("0")
        purchased_items = OrderItem.objects.filter(order__user=user).aggregate(total=Sum("quantity"))["total"] or 0
        top_products = list(
            OrderItem.objects.filter(order__user=user, product__isnull=False)
            .values("product__name")
            .annotate(total=Count("id"))
            .order_by("-total", "product__name")[:5]
        )
        recent_reviews = [
            {
                "product_name": review.product.name,
                "product_url": reverse("products:detail", kwargs={"slug": review.product.slug}),
                "rating": review.rating,
                "comment": review.comment,
                "created_at": date_format(localtime(review.created_at), "d.m.Y"),
            }
            for review in Review.objects.filter(user=user, is_active=True).select_related("product")[:5]
        ]

        display_first_name = payload.first_name or user.username
        display_last_name = payload.last_name
        initials = profile.get_initials()

        # request.user can be AnonymousUser in type hint, but this service expects authenticated user
        user_date_joined = getattr(user, "date_joined", None)
        joined_at = user_date_joined.date() if user_date_joined else date.today()

        return {
            "client_page_title": _("My Cabinet"),
            "profile": profile,
            "profile_form": {
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "patronymic": payload.patronymic,
                "phone": payload.phone,
                "email": payload.email,
                "birth_date": payload.birth_date,
            },
            "corner_summary": {
                "display_name": " ".join(part for part in [display_first_name, display_last_name] if part).strip(),
                "subtitle": _("Client since %(month)s %(year)s")
                % {"month": joined_at.strftime("%B"), "year": joined_at.year},
                "initials": initials,
                "stats": [
                    ClientSummaryCard(label=str(_("Orders")), value=str(orders_total_count)),
                    ClientSummaryCard(label=str(_("Spent")), value=f"{spent_total:.2f}"),
                    ClientSummaryCard(label=str(_("Items Bought")), value=str(purchased_items)),
                ],
            },
            "orders_table": cls._build_orders_table(order_rows),
            "orders_total_count": orders_total_count,
            "orders_visible_count": len(order_rows),
            "active_orders_count": active_orders_count,
            "delivered_orders_count": orders_queryset.filter(status="delivered").count(),
            "cancelled_orders_count": orders_queryset.filter(status="cancelled").count(),
            "top_products": [item["product__name"] for item in top_products],
            "reviews_total_count": Review.objects.filter(user=user, is_active=True).count(),
            "recent_reviews": recent_reviews,
        }

    @classmethod
    def save_corner_profile(cls, request: HttpRequest) -> tuple[bool, str]:
        user = cast("User", request.user)
        from system.services.client_profile import ClientProfilePayload

        clean_data, error = ClientProfileService.parse_form_data(request.POST)
        if error:
            return False, error

        payload = ClientProfilePayload(**clean_data)
        return ClientProfileService.save_profile(user, payload)

    @classmethod
    def get_appointments_context(cls, request: HttpRequest) -> dict[str, object]:
        user = cast("User", request.user)
        orders = list(Order.objects.filter(user=user).order_by("-created_at"))
        active_orders = [order for order in orders if order.status not in cls.CLOSED_ORDER_STATUSES]
        history_orders = [order for order in orders if order.status in cls.CLOSED_ORDER_STATUSES]

        return {
            "client_page_title": _("My Orders"),
            "order_stats": [
                MetricWidgetData(
                    label=str(_("Active")),
                    value=str(len(active_orders)),
                    trend_label=str(_("in progress")),
                    icon="bi-bag-check",
                ),
                MetricWidgetData(
                    label=str(_("Delivered")),
                    value=str(sum(1 for order in history_orders if order.status == "delivered")),
                    trend_label=str(_("completed orders")),
                    icon="bi-check-circle",
                ),
                MetricWidgetData(
                    label=str(_("Cancelled")),
                    value=str(sum(1 for order in history_orders if order.status == "cancelled")),
                    trend_label=str(_("closed orders")),
                    icon="bi-x-circle",
                ),
            ],
            "active_orders_table": cls._build_orders_table(cls._build_order_rows(active_orders)),
            "history_table": cls._build_orders_table(cls._build_order_rows(history_orders)),
            "active_orders_total_count": len(active_orders),
            "active_orders_visible_count": len(active_orders),
            "history_total_count": len(history_orders),
            "history_visible_count": len(history_orders),
        }
