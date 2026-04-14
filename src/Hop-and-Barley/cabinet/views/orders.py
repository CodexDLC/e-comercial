from __future__ import annotations

from typing import Any
from uuid import UUID

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

from cabinet.services.orders import OrderCabinetService
from features.orders.services.order import OrderService


class OrdersManagementView(TemplateView):
    """View to list all orders for staff."""

    template_name = "cabinet/orders/list.html"
    module_name = "orders"

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_module = self.module_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get("status")
        context.update(OrderCabinetService.get_list_data(status_filter=status_filter))
        context.update({
            "header_title": str(_("Orders")),
            "header_subtitle": str(_("Order Management")),
        })
        # Status choices needed for the filter and the dropdown
        from features.orders.models.order import Order

        context["status_choices"] = Order.STATUS_CHOICES
        return context


class OrderDetailView(TemplateView):
    """View to show full order detail for staff processing."""

    template_name = "cabinet/orders/detail.html"
    module_name = "orders"

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_module = self.module_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_id: UUID = self.kwargs["pk"]
        data = OrderCabinetService.get_detail_data(order_id)
        context.update(data)
        context.update({
            "header_title": f"Order #{str(data['order'].id)[:8].upper()}",
            "header_subtitle": str(_("Order Details")),
        })
        from features.orders.models.order import Order
        context["status_choices"] = Order.STATUS_CHOICES
        return context


class OrderStatusUpdateView(View):
    """HTMX view to update the status of an order."""

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        order_id = self.kwargs.get("pk")
        new_status = request.POST.get("status")

        if order_id and new_status:
            OrderService.update_status(order_id, new_status)

        if request.headers.get("HX-Request"):
            # If called from detail page — reload detail, else just trigger list refresh
            referer = request.headers.get("HX-Current-URL", "")
            if "orders/" in referer and str(order_id) in referer:
                from django.shortcuts import redirect
                response = HttpResponse(status=204)
                response["HX-Redirect"] = str(reverse_lazy("cabinet:orders_detail", kwargs={"pk": order_id}))
                return response
            return HttpResponse(status=204, headers={"HX-Trigger": "refreshTable"})

        from django.shortcuts import redirect
        return redirect(reverse_lazy("cabinet:orders_list"))
