from datetime import timedelta
from urllib.parse import urlencode

from codex_django.cabinet import (
    DashboardWidget,
    MetricWidgetData,
    SidebarItem,
    TopbarEntry,
    cabinet_registry,
    declare,
)
from codex_django.cabinet.selector.dashboard import DashboardSelector
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


def _with_query(url: object, **params: str) -> object:
    return format_lazy("{}?{}", url, urlencode(params))


@DashboardSelector.extend(cache_key="user_summary", cache_ttl=0)
def provide_user_summary_kpi(request: HttpRequest) -> dict[str, MetricWidgetData]:
    total_count = User.objects.count()
    last_week = timezone.now() - timedelta(days=7)
    new_count = User.objects.filter(date_joined__gte=last_week).count()

    topbar = cabinet_registry.get_module_topbar("users")
    base_label = str(topbar.label) if topbar else str(_("Users"))
    display_label = str(_("Total {label}")).format(label=base_label).upper()

    return {
        "user_summary_kpi": MetricWidgetData(
            label=display_label,
            value=str(total_count),
            trend_value=f"+{new_count}",
            trend_direction="up",
            trend_label=str(_("this week")),
            icon="bi-people",
            url=reverse_lazy("cabinet:users_list"),
        )
    }


declare(
    module="analytics",
    space="staff",
    topbar=TopbarEntry(
        group="admin",
        label=str(_("Analytics")),
        icon="bi-graph-up",
        url=reverse_lazy("cabinet:analytics_dashboard"),
        order=10,
    ),
    sidebar=[
        SidebarItem(
            label=str(_("Dashboard")),
            url=reverse_lazy("cabinet:analytics_dashboard"),
            icon="bi-speedometer2",
            order=1,
        ),
        SidebarItem(
            label=str(_("Reports")),
            url=reverse_lazy("cabinet:analytics_reports"),
            icon="bi-file-bar-graph",
            order=2,
        ),
    ],
    dashboard_widgets=[
        DashboardWidget(
            template="cabinet/widgets/chart.html",
            context_key="revenue_chart",
            col="col-xl-8 col-lg-7",
            order=30,
        ),
        DashboardWidget(
            template="cabinet/widgets/chart.html",
            context_key="orders_chart",
            col="col-xl-4 col-lg-5",
            order=31,
        ),
        DashboardWidget(
            template="cabinet/widgets/donut.html",
            context_key="orders_donut",
            col="col-xl-4 col-lg-5",
            order=33,
        ),
        DashboardWidget(
            template="cabinet/widgets/list.html",
            context_key="top_products",
            col="col-xl-4 col-lg-6",
            order=34,
        ),
        DashboardWidget(
            template="cabinet/widgets/list.html",
            context_key="recent_orders",
            col="col-xl-4 col-lg-6",
            order=35,
        ),
    ],
)


declare(
    module="users",
    space="staff",
    topbar=TopbarEntry(
        group="admin",
        label=str(_("Users")),
        icon="bi-people",
        url=reverse_lazy("cabinet:users_list"),
        order=20,
    ),
    sidebar=[
        SidebarItem(
            label=str(_("All Users")),
            url=reverse_lazy("cabinet:users_list"),
            icon="bi-person-lines-fill",
            order=1,
        ),
        SidebarItem(
            label=str(_("Only Users")),
            url=_with_query(reverse_lazy("cabinet:users_list"), segment="clients"),
            icon="bi-person-check",
            order=2,
        ),
        SidebarItem(
            label=str(_("Staff Only")),
            url=_with_query(reverse_lazy("cabinet:users_list"), segment="staff"),
            icon="bi-shield-lock",
            order=3,
        ),
    ],
    dashboard_widgets=[
        DashboardWidget(
            template="cabinet/widgets/kpi.html",
            context_key="user_summary_kpi",
            col="col-lg-3",
            order=10,
        )
    ],
)


declare(
    module="client",
    space="client",
    sidebar=[
        SidebarItem(
            label=str(_("My Orders")),
            url=reverse_lazy("cabinet:client_orders"),
            icon="bi-bag-check",
            order=1,
        ),
        SidebarItem(
            label=str(_("My Cabinet")),
            url=reverse_lazy("cabinet:client_home"),
            icon="bi-person",
            order=2,
        ),
    ],
)
