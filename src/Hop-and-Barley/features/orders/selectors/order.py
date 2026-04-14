from __future__ import annotations

from django.db.models import QuerySet

from features.orders.models import Order


class OrderSelector:
    """Read operations for Order models."""

    @classmethod
    def get_orders_list(cls, status_filter: str | None = None) -> QuerySet[Order]:
        qs = Order.objects.select_related("user").order_by("-created_at")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs
