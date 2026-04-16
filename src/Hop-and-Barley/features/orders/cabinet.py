from codex_django.cabinet import DashboardWidget, MetricWidgetData, SidebarItem, TopbarEntry, declare
from codex_django.cabinet.notifications import notification_registry
from codex_django.cabinet.selector.dashboard import DashboardSelector
from django.http import HttpRequest
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from features.orders.models.order import Order


@notification_registry.register("orders")
def _orders_bell(request: HttpRequest) -> object:
    from codex_django.conversations.cabinet import build_inbox_notification_item

    count = Order.objects.filter(status="pending").count()
    return build_inbox_notification_item(
        count=count,
        url=reverse("cabinet:orders_list") + "?status=pending",
        label=str(_("New orders")),
    )


@DashboardSelector.extend(cache_key="orders_stats", cache_ttl=0)
def provide_orders_stats(request: HttpRequest) -> dict[str, MetricWidgetData]:
    pending = Order.objects.filter(status="pending").count()
    total = Order.objects.count()
    return {
        "orders_stats": MetricWidgetData(
            label=str(_("Orders")),
            value=str(total),
            trend_value=f"{_('pending')}: {pending}",
            trend_direction="up" if pending > 0 else "neutral",
            trend_label=str(_("awaiting processing")),
            icon="bi-bag-check",
            url=reverse("cabinet:orders_list"),
        )
    }


declare(
    module="orders",
    space="staff",
    topbar=TopbarEntry(
        group="services",
        label=str(_("Orders")),
        icon="bi-bag-check",
        url=reverse_lazy("cabinet:orders_list"),
        order=10,
    ),
    sidebar=[
        SidebarItem(
            label=str(_("Queue")),
            url=reverse_lazy("cabinet:orders_list") + "?status=pending",
            icon="bi-clock",
            order=1,
        ),
        SidebarItem(
            label=str(_("All Orders")),
            url=reverse_lazy("cabinet:orders_list"),
            icon="bi-list-ul",
            order=2,
        ),
        SidebarItem(
            label=str(_("Processing")),
            url=reverse_lazy("cabinet:orders_list") + "?status=processing",
            icon="bi-gear",
            order=3,
        ),
        SidebarItem(
            label=str(_("Shipped")),
            url=reverse_lazy("cabinet:orders_list") + "?status=shipped",
            icon="bi-truck",
            order=4,
        ),
    ],
    dashboard_widgets=[
        DashboardWidget(
            template="cabinet/widgets/kpi.html",
            context_key="orders_stats",
            col="col-lg-3",
            order=5,
        )
    ],
)
