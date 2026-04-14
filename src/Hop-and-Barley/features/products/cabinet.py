from typing import Any

from codex_django.cabinet import DashboardWidget, SidebarItem, TopbarEntry, declare
from codex_django.cabinet.selector.dashboard import DashboardSelector
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from cabinet.services.product import ProductCabinetService


@DashboardSelector.extend(cache_key="product_metrics", cache_ttl=0)
def provide_product_kpis(request: HttpRequest) -> dict[str, Any]:
    """Provides product-related metrics for the staff dashboard."""
    metrics = ProductCabinetService.get_dashboard_metrics()
    return {
        "product_total_kpi": metrics[0],
        "product_stock_kpi": metrics[1],
    }


declare(
    module="products",
    space="staff",
    topbar=TopbarEntry(
        group="admin",
        label=str(_("Products")),
        icon="bi-box-seam",
        url=reverse_lazy("cabinet:product_catalog"),
        order=15,
    ),
    sidebar=[
        SidebarItem(
            label=str(_("All Catalog")),
            url=reverse_lazy("cabinet:product_catalog"),
            icon="bi-table",
            order=1,
        ),
        SidebarItem(
            label=str(_("Hops")),
            url=str(reverse_lazy("cabinet:product_catalog")) + "?category=hops",
            icon="bi-tag",
            order=2,
        ),
        SidebarItem(
            label=str(_("Malts")),
            url=str(reverse_lazy("cabinet:product_catalog")) + "?category=malts",
            icon="bi-tag",
            order=3,
        ),
        SidebarItem(
            label=str(_("Yeast")),
            url=str(reverse_lazy("cabinet:product_catalog")) + "?category=yeast",
            icon="bi-tag",
            order=4,
        ),
        SidebarItem(
            label=str(_("Brewing Kits")),
            url=str(reverse_lazy("cabinet:product_catalog")) + "?category=brewing-kits",
            icon="bi-tag",
            order=5,
        ),
    ],
    dashboard_widgets=[
        DashboardWidget(
            template="cabinet/widgets/kpi.html",
            context_key="product_total_kpi",
            col="col-lg-3",
            order=20,
        ),
        DashboardWidget(
            template="cabinet/widgets/kpi.html",
            context_key="product_stock_kpi",
            col="col-lg-3",
            order=21,
        ),
    ],
)
