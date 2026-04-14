from typing import Any

from codex_django.cabinet.selector.dashboard import DashboardSelector
from django.http import HttpRequest

from cabinet.services.product import ProductCabinetService


@DashboardSelector.extend(cache_key="product_metrics", cache_ttl=0)
def provide_product_kpis(request: HttpRequest) -> dict[str, Any]:
    """Provides product-related metrics for the staff dashboard."""
    metrics = ProductCabinetService.get_dashboard_metrics()
    # metrics[0] is Total, metrics[1] is Out of Stock
    return {
        "product_total_kpi": metrics[0],
        "product_stock_kpi": metrics[1],
    }
