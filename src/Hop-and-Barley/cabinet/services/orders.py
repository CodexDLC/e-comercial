from __future__ import annotations

from typing import Any
from uuid import UUID

from django.shortcuts import get_object_or_404

from features.orders.models.order import Order
from features.orders.selectors.order import OrderSelector

STATUS_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}

STATUS_ICONS: dict[str, str] = {
    "processing": "bi-gear",
    "shipped": "bi-truck",
    "delivered": "bi-check2-circle",
    "cancelled": "bi-x-circle",
}

STATUS_STYLES: dict[str, str] = {
    "processing": "btn-primary",
    "shipped": "btn-info",
    "delivered": "btn-success",
    "cancelled": "btn-danger",
}


class OrderCabinetService:
    """Service for transforming order data into Cabinet UI types."""

    @classmethod
    def get_list_data(cls, status_filter: str | None = None) -> dict[str, Any]:
        queryset = OrderSelector.get_orders_list(status_filter=status_filter)

        return {
            "orders": queryset,
            "active_status": status_filter,
        }

    @classmethod
    def get_detail_data(cls, order_id: UUID) -> dict[str, Any]:
        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related("items__product"),
            pk=order_id,
        )
        next_statuses = STATUS_TRANSITIONS.get(order.status, [])
        transitions = [
            {
                "value": s,
                "label": dict(Order.STATUS_CHOICES).get(s, s),
                "icon": STATUS_ICONS.get(s, "bi-arrow-right"),
                "btn_class": STATUS_STYLES.get(s, "btn-secondary"),
            }
            for s in next_statuses
        ]
        return {
            "order": order,
            "items": order.items.select_related("product").all(),
            "transitions": transitions,
        }
