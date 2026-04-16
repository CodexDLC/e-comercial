from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from codex_django.cabinet.selector.dashboard import DashboardSelector
from codex_django.cabinet.types.widgets import ListItem, ListWidgetData, MetricWidgetData
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from features.conversations.models import Message
from features.orders.models import Order, OrderItem
from features.products.models import Product


@dataclass
class AnalyticsService:
    REPORT_TABS: tuple[dict[str, str], ...] = (
        {"key": "revenue", "label": "Revenue", "icon": "bi-currency-dollar"},
        {"key": "products", "label": "Products", "icon": "bi-box-seam"},
        {"key": "customers", "label": "Customers", "icon": "bi-people"},
    )

    PERIOD_OPTIONS: tuple[dict[str, str], ...] = (
        {"key": "week", "label": "Week"},
        {"key": "month", "label": "Month"},
        {"key": "quarter", "label": "Quarter"},
    )

    @staticmethod
    def get_kpi_metrics() -> dict[str, MetricWidgetData]:
        User = get_user_model()
        sales_agg = Order.objects.aggregate(total=Sum("total_price"))
        kpi_sales = sales_agg["total"] or 0
        kpi_users = User.objects.count()
        kpi_orders = Order.objects.count()
        kpi_pending = Order.objects.filter(status="pending").count()

        return {
            "revenue": MetricWidgetData(
                label=str(_("Total Sales")),
                value=f"{kpi_sales:,.0f}".replace(",", " "),
                unit="$",
                trend_value="",
                trend_direction="",
                icon="bi-currency-dollar",
            ),
            "users": MetricWidgetData(
                label=str(_("Total Users")),
                value=str(kpi_users),
                trend_value="",
                trend_direction="",
                icon="bi-people",
            ),
            "orders": MetricWidgetData(
                label=str(_("Total Orders")),
                value=str(kpi_orders),
                trend_value="",
                trend_direction="",
                icon="bi-cart",
            ),
            "pending": MetricWidgetData(
                label=str(_("Total Pending")),
                value=str(kpi_pending),
                trend_value="",
                trend_direction="",
                icon="bi-clock",
            ),
            "open_messages": MetricWidgetData(
                label=str(_("Active Messages")),
                value=str(Message.objects.filter(status="open").count()),
                trend_value="",
                trend_direction="",
                icon="bi-envelope",
            ),
        }

    @staticmethod
    def _format_currency(value: Decimal | float | int | None) -> str:
        amount = Decimal(value or 0)
        return f"${amount:,.2f}"

    @staticmethod
    def _format_percent(value: Decimal | float | int | None) -> str:
        amount = Decimal(value or 0)
        return f"{amount:.1f}%"

    @staticmethod
    def _get_period_bounds(period: str, today: date) -> tuple[date, date]:
        normalized = period if period in {"week", "month", "quarter"} else "month"
        if normalized == "week":
            return today - timedelta(days=6), today
        if normalized == "quarter":
            # Standard calendar quarters (Q1, Q2, Q3, Q4)
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            return date(today.year, quarter_start_month, 1), today
        return today.replace(day=1), today

    @staticmethod
    def _get_previous_period(date_from: date, date_to: date) -> tuple[date, date]:
        span_days = (date_to - date_from).days + 1
        prev_end = date_from - timedelta(days=1)
        prev_start = prev_end - timedelta(days=span_days - 1)
        return prev_start, prev_end

    @staticmethod
    def _get_day_labels(date_from: date, date_to: date) -> list[date]:
        return [date_from + timedelta(days=index) for index in range((date_to - date_from).days + 1)]

    @staticmethod
    def _build_daily_rows(
        date_from: date,
        date_to: date,
        *,
        orders_map: dict[date, int] | None = None,
        revenue_map: dict[date, Decimal] | None = None,
        users_map: dict[date, int] | None = None,
        message_map: dict[date, int] | None = None,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for day in AnalyticsService._get_day_labels(date_from, date_to):
            orders_count = (orders_map or {}).get(day, 0)
            revenue = Decimal((revenue_map or {}).get(day, 0))
            users_count = (users_map or {}).get(day, 0)
            message_count = (message_map or {}).get(day, 0)
            avg_order = revenue / orders_count if orders_count else Decimal("0")
            rows.append(
                {
                    "label": day.strftime("%d.%m"),
                    "revenue_fmt": AnalyticsService._format_currency(revenue),
                    "orders": orders_count,
                    "avg_order_fmt": AnalyticsService._format_currency(avg_order),
                    "new_users": users_count,
                    "messages": message_count,
                }
            )
        return rows

    @staticmethod
    def _revenue_decimal_by_day(date_from: date, date_to: date) -> dict[date, Decimal]:
        return {
            row["day"]: row["total"] or Decimal("0")
            for row in Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Sum("total_price"))
        }

    @staticmethod
    def _users_by_day(date_from: date, date_to: date) -> dict[date, int]:
        User = get_user_model()
        return {
            row["day"]: row["count"]
            for row in User.objects.filter(date_joined__date__gte=date_from, date_joined__date__lte=date_to)
            .annotate(day=TruncDate("date_joined"))
            .values("day")
            .annotate(count=Count("id"))
        }

    @staticmethod
    def _messages_by_day(date_from: date, date_to: date) -> dict[date, int]:
        return {
            row["day"]: row["count"]
            for row in Message.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
        }

    @staticmethod
    def _get_revenue_report_context(
        date_from: date, date_to: date, previous_from: date, previous_to: date
    ) -> dict[str, object]:
        orders_qs = Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
        previous_orders_qs = Order.objects.filter(
            created_at__date__gte=previous_from, created_at__date__lte=previous_to
        )

        total_revenue = orders_qs.aggregate(total=Sum("total_price"))["total"] or Decimal("0")
        total_orders = orders_qs.count()
        previous_revenue = previous_orders_qs.aggregate(total=Sum("total_price"))["total"] or Decimal("0")
        average_order = orders_qs.aggregate(avg=Avg("total_price"))["avg"] or Decimal("0")
        delivered_count = orders_qs.filter(status="delivered").count()
        delivered_rate = (Decimal(delivered_count) / Decimal(total_orders) * 100) if total_orders else Decimal("0")

        orders_map = AnalyticsService._orders_by_day(date_from, date_to)
        revenue_map = AnalyticsService._revenue_decimal_by_day(date_from, date_to)
        rows = AnalyticsService._build_daily_rows(
            date_from,
            date_to,
            orders_map=orders_map,
            revenue_map=revenue_map,
        )
        revenue_values = [
            float(revenue_map.get(day, Decimal("0"))) for day in AnalyticsService._get_day_labels(date_from, date_to)
        ]
        order_values = [orders_map.get(day, 0) for day in AnalyticsService._get_day_labels(date_from, date_to)]
        growth = ((total_revenue - previous_revenue) / previous_revenue) * 100 if previous_revenue else Decimal("0")

        return {
            "report_summary": str(_("Revenue, order volume, and average чек for the selected period.")),
            "summary_cards": [
                {
                    "label": str(_("Revenue")),
                    "value": AnalyticsService._format_currency(total_revenue),
                    "hint": str(_("Gross sales")),
                },
                {"label": str(_("Orders")), "value": str(total_orders), "hint": str(_("Completed and in-progress"))},
                {
                    "label": str(_("Average Order")),
                    "value": AnalyticsService._format_currency(average_order),
                    "hint": str(_("Average order value")),
                },
                {
                    "label": str(_("Delivered Rate")),
                    "value": AnalyticsService._format_percent(delivered_rate),
                    "hint": str(_("Share of delivered orders")),
                },
            ],
            "chart_type": "line",
            "chart_title": str(_("Revenue Trend")),
            "chart_description": str(_("Revenue and order volume for the selected period.")),
            "chart_labels": [row["label"] for row in rows],
            "chart_datasets": [
                {
                    "label": str(_("Revenue")),
                    "data": revenue_values,
                    "borderColor": "#2563eb",
                    "backgroundColor": "rgba(37,99,235,0.12)",
                    "fill": True,
                    "tension": 0.35,
                    "yAxisID": "y",
                },
                {
                    "label": str(_("Orders")),
                    "data": order_values,
                    "borderColor": "#0f172a",
                    "backgroundColor": "rgba(15,23,42,0.15)",
                    "fill": False,
                    "tension": 0.2,
                    "yAxisID": "y1",
                },
            ],
            "columns": [
                {"key": "label", "label": str(_("Day")), "bold": True},
                {"key": "revenue_fmt", "label": str(_("Revenue")), "align": "right"},
                {"key": "orders", "label": str(_("Orders")), "align": "right"},
                {"key": "avg_order_fmt", "label": str(_("Average Order")), "align": "right"},
            ],
            "rows": rows,
            "summary_row": {
                "label": str(_("Total")),
                "revenue_fmt": AnalyticsService._format_currency(total_revenue),
                "orders": total_orders,
                "avg_order_fmt": AnalyticsService._format_currency(average_order),
            },
            "table_summary": {
                "primary": AnalyticsService._format_currency(total_revenue),
                "secondary": str(
                    _("Growth vs previous period: %(value)s") % {"value": AnalyticsService._format_percent(growth)}
                ),
            },
        }

    @staticmethod
    def _get_products_report_context(date_from: date, date_to: date) -> dict[str, object]:
        revenue_expr = ExpressionWrapper(
            F("quantity") * F("price"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        item_qs = (
            OrderItem.objects.filter(order__created_at__date__gte=date_from, order__created_at__date__lte=date_to)
            .values("product__name")
            .annotate(
                units=Sum("quantity"),
                revenue=Sum(revenue_expr),
                avg_price=Avg("price"),
                order_count=Count("order", distinct=True),
            )
            .order_by("-revenue", "-units", "product__name")
        )
        rows = [
            {
                "label": row["product__name"] or str(_("Unknown product")),
                "units": row["units"] or 0,
                "revenue_fmt": AnalyticsService._format_currency(row["revenue"]),
                "avg_price_fmt": AnalyticsService._format_currency(row["avg_price"]),
            }
            for row in item_qs[:10]
        ]
        total_units = sum(int(row["units"] or 0) for row in item_qs)
        total_revenue = sum(Decimal(row["revenue"] or 0) for row in item_qs)
        active_products = Product.objects.filter(is_active=True).count()
        top_product_name = rows[0]["label"] if rows else str(_("No sales yet"))

        return {
            "report_summary": str(_("Top-selling products and revenue contribution by item.")),
            "summary_cards": [
                {"label": str(_("Units Sold")), "value": str(total_units), "hint": str(_("Across all order items"))},
                {
                    "label": str(_("Item Revenue")),
                    "value": AnalyticsService._format_currency(total_revenue),
                    "hint": str(_("Revenue attributed to products")),
                },
                {
                    "label": str(_("Active Products")),
                    "value": str(active_products),
                    "hint": str(_("Visible in catalog")),
                },
                {
                    "label": str(_("Top Product")),
                    "value": top_product_name,
                    "hint": str(_("Highest revenue in period")),
                },
            ],
            "chart_type": "bar",
            "chart_title": str(_("Product Revenue")),
            "chart_description": str(_("Top products ranked by revenue.")),
            "chart_labels": [row["label"] for row in rows[:8]],
            "chart_datasets": [
                {
                    "label": str(_("Revenue")),
                    "data": [float(Decimal(item_qs_row["revenue"] or 0)) for item_qs_row in item_qs[:8]],
                    "backgroundColor": "rgba(22,163,74,0.75)",
                    "borderRadius": 8,
                }
            ],
            "columns": [
                {"key": "label", "label": str(_("Product")), "bold": True},
                {"key": "units", "label": str(_("Units")), "align": "right"},
                {"key": "revenue_fmt", "label": str(_("Revenue")), "align": "right"},
                {"key": "avg_price_fmt", "label": str(_("Average Price")), "align": "right"},
            ],
            "rows": rows,
            "summary_row": {
                "label": str(_("Total")),
                "units": total_units,
                "revenue_fmt": AnalyticsService._format_currency(total_revenue),
                "avg_price_fmt": "—",
            },
            "table_summary": {
                "primary": AnalyticsService._format_currency(total_revenue),
                "secondary": str(_("Units sold: %(value)s") % {"value": total_units}),
            },
        }

    @staticmethod
    def _get_customers_report_context(date_from: date, date_to: date) -> dict[str, object]:
        User = get_user_model()
        users_qs = User.objects.filter(date_joined__date__gte=date_from, date_joined__date__lte=date_to)
        orders_qs = Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
        messages_qs = Message.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)

        new_users = users_qs.count()
        active_customers = orders_qs.exclude(user__isnull=True).values("user").distinct().count()
        repeat_customers = (
            orders_qs.exclude(user__isnull=True)
            .values("user")
            .annotate(order_count=Count("id"))
            .filter(order_count__gt=1)
            .count()
        )
        open_messages = messages_qs.filter(status=Message.Status.OPEN).count()

        orders_map = AnalyticsService._orders_by_day(date_from, date_to)
        users_map = AnalyticsService._users_by_day(date_from, date_to)
        message_map = AnalyticsService._messages_by_day(date_from, date_to)
        revenue_map = AnalyticsService._revenue_decimal_by_day(date_from, date_to)
        rows = AnalyticsService._build_daily_rows(
            date_from,
            date_to,
            orders_map=orders_map,
            users_map=users_map,
            message_map=message_map,
            revenue_map=revenue_map,
        )

        return {
            "report_summary": str(_("Customer acquisition, repeat buyers, and support activity.")),
            "summary_cards": [
                {"label": str(_("New Users")), "value": str(new_users), "hint": str(_("Joined in selected period"))},
                {
                    "label": str(_("Active Customers")),
                    "value": str(active_customers),
                    "hint": str(_("Placed at least one order")),
                },
                {
                    "label": str(_("Repeat Customers")),
                    "value": str(repeat_customers),
                    "hint": str(_("Placed multiple orders")),
                },
                {
                    "label": str(_("Open Messages")),
                    "value": str(open_messages),
                    "hint": str(_("Inbound support still open")),
                },
            ],
            "chart_type": "line",
            "chart_title": str(_("Customer Activity")),
            "chart_description": str(_("New users, active customers, and message volume over time.")),
            "chart_labels": [row["label"] for row in rows],
            "chart_datasets": [
                {
                    "label": str(_("New Users")),
                    "data": [row["new_users"] for row in rows],
                    "borderColor": "#7c3aed",
                    "backgroundColor": "rgba(124,58,237,0.12)",
                    "fill": True,
                    "tension": 0.35,
                },
                {
                    "label": str(_("Orders")),
                    "data": [row["orders"] for row in rows],
                    "borderColor": "#0ea5e9",
                    "backgroundColor": "rgba(14,165,233,0.10)",
                    "fill": False,
                    "tension": 0.25,
                },
                {
                    "label": str(_("Messages")),
                    "data": [row["messages"] for row in rows],
                    "borderColor": "#f97316",
                    "backgroundColor": "rgba(249,115,22,0.10)",
                    "fill": False,
                    "tension": 0.25,
                },
            ],
            "columns": [
                {"key": "label", "label": str(_("Day")), "bold": True},
                {"key": "new_users", "label": str(_("New Users")), "align": "right"},
                {"key": "orders", "label": str(_("Orders")), "align": "right"},
                {"key": "messages", "label": str(_("Messages")), "align": "right"},
            ],
            "rows": rows,
            "summary_row": {
                "label": str(_("Total")),
                "new_users": new_users,
                "orders": orders_qs.count(),
                "messages": messages_qs.count(),
            },
            "table_summary": {
                "primary": str(active_customers),
                "secondary": str(_("Repeat customers: %(value)s") % {"value": repeat_customers}),
            },
        }

    @staticmethod
    def _revenue_by_day(date_from: date, date_to: date) -> dict[date, float]:
        return {
            row["day"]: float(row["total"] or 0)
            for row in Order.objects.filter(
                created_at__date__gte=date_from,
                created_at__date__lte=date_to,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Sum("total_price"))
        }

    @staticmethod
    def _orders_by_day(date_from: date, date_to: date) -> dict[date, int]:
        return {
            row["day"]: row["count"]
            for row in Order.objects.filter(
                created_at__date__gte=date_from,
                created_at__date__lte=date_to,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
        }

    @staticmethod
    def get_chart_data() -> dict[str, dict[str, Any]]:
        today = timezone.now().date()

        # Current month
        cur_start = today.replace(day=1)
        cur_days = [cur_start + timedelta(days=i) for i in range((today - cur_start).days + 1)]

        # Previous month (same number of days)
        prev_end = cur_start - timedelta(days=1)
        prev_start = prev_end.replace(day=1)
        prev_days = [prev_start + timedelta(days=i) for i in range((prev_end - prev_start).days + 1)]

        cur_rev = AnalyticsService._revenue_by_day(cur_start, today)
        prev_rev = AnalyticsService._revenue_by_day(prev_start, prev_end)

        cur_ord = AnalyticsService._orders_by_day(cur_start, today)
        prev_ord = AnalyticsService._orders_by_day(prev_start, prev_end)

        # Labels aligned by day-of-month (use current month length)
        max_days = max(len(cur_days), len(prev_days))
        labels = [str(i + 1) for i in range(max_days)]

        def pad(day_list: list[date], mapping: dict[date, int | float]) -> list[int | float | None]:
            return [mapping.get(d, 0) for d in day_list] + [None] * (max_days - len(day_list))

        cur_rev_data = pad(cur_days, cur_rev)
        prev_rev_data = pad(prev_days, prev_rev)
        cur_ord_data = pad(cur_days, cur_ord)
        prev_ord_data = pad(prev_days, prev_ord)

        total_cur = sum(v for v in cur_rev_data if v)
        total_prev = sum(v for v in prev_rev_data if v)
        trend_pct = ((total_cur - total_prev) / total_prev * 100) if total_prev else 0
        trend_sign = "+" if trend_pct >= 0 else ""

        orders_cur_total = sum(v for v in cur_ord_data if v)
        orders_prev_total = sum(v for v in prev_ord_data if v)
        orders_trend = ((orders_cur_total - orders_prev_total) / orders_prev_total * 100) if orders_prev_total else 0
        orders_sign = "+" if orders_trend >= 0 else ""

        # Status donut
        status_keys = ["pending", "processing", "shipped", "delivered", "cancelled"]
        status_labels = [
            str(_("Pending")),
            str(_("Processing")),
            str(_("Shipped")),
            str(_("Delivered")),
            str(_("Cancelled")),
        ]
        status_colors = ["#f59e0b", "#3b82f6", "#06b6d4", "#22c55e", "#ef4444"]
        status_counts = {
            row["status"]: row["count"] for row in Order.objects.values("status").annotate(count=Count("id"))
        }
        donut_data = [status_counts.get(k, 0) for k in status_keys]

        cur_month_label = cur_start.strftime("%B")
        prev_month_label = prev_start.strftime("%B")

        return {
            "revenue_chart": {
                "chart_id": "revenueChart",
                "title": str(_("Revenue")),
                "subtitle": cur_month_label,
                "icon": "bi-graph-up",
                "type": "line",
                "kpi_value": f"${total_cur:,.2f}",
                "kpi_trend": f"{trend_sign}{trend_pct:.1f}%",
                "kpi_trend_label": f"vs {prev_month_label}",
                "show_legend": True,
                "chart_labels": labels,
                "datasets": [
                    {
                        "label": cur_month_label,
                        "data": cur_rev_data,
                        "borderColor": "#4f46e5",
                        "backgroundColor": "rgba(79,70,229,0.08)",
                        "fill": True,
                        "tension": 0.4,
                        "borderWidth": 2,
                        "pointRadius": 2,
                    },
                    {
                        "label": prev_month_label,
                        "data": prev_rev_data,
                        "borderColor": "#94a3b8",
                        "backgroundColor": "rgba(148,163,184,0.0)",
                        "fill": False,
                        "tension": 0.4,
                        "borderWidth": 1.5,
                        "borderDash": [4, 4],
                        "pointRadius": 0,
                    },
                ],
            },
            "orders_chart": {
                "chart_id": "ordersChart",
                "title": str(_("Orders")),
                "subtitle": cur_month_label,
                "icon": "bi-bag-check",
                "type": "bar",
                "kpi_value": str(orders_cur_total),
                "kpi_trend": f"{orders_sign}{orders_trend:.1f}%",
                "kpi_trend_label": f"vs {prev_month_label}",
                "show_legend": True,
                "chart_labels": labels,
                "datasets": [
                    {
                        "label": cur_month_label,
                        "data": cur_ord_data,
                        "backgroundColor": "rgba(79,70,229,0.7)",
                        "borderRadius": 4,
                        "borderWidth": 0,
                    },
                    {
                        "label": prev_month_label,
                        "data": prev_ord_data,
                        "backgroundColor": "rgba(148,163,184,0.35)",
                        "borderRadius": 4,
                        "borderWidth": 0,
                    },
                ],
            },
            "orders_donut": {
                "chart_id": "ordersDonut",
                "title": str(_("Orders by Status")),
                "icon": "bi-pie-chart",
                "chart_labels": status_labels,
                "chart_data": donut_data,
                "colors": status_colors,
            },
        }

    @staticmethod
    def get_top_lists() -> dict[str, ListWidgetData]:
        top_items = OrderItem.objects.values("product__name").annotate(total=Sum("quantity")).order_by("-total")[:5]
        top_products_items = [
            ListItem(
                label=item["product__name"] or str(_("Unknown")),
                value=str(item["total"]),
                sublabel=str(_("units sold")),
            )
            for item in top_items
        ]

        latest_orders = Order.objects.order_by("-created_at").select_related("user")[:5]
        recent_orders_items = [
            ListItem(
                label=f"Order {order.id.hex[:8]}",
                value=f"${order.total_price:,.2f}",
                sublabel=order.get_status_display(),
            )
            for order in latest_orders
        ]

        return {
            "top_products": ListWidgetData(
                title=str(_("Top Products")),
                subtitle=str(_("By quantity sold")),
                icon="bi-star",
                items=top_products_items,
            ),
            "recent_orders": ListWidgetData(
                title=str(_("Recent Orders")),
                subtitle=str(_("Latest 5 orders")),
                icon="bi-cart",
                items=recent_orders_items,
            ),
        }

    @staticmethod
    def get_reports_context(request: HttpRequest) -> dict[str, object]:
        """Return the complete reports page contract for cabinet analytics."""
        tab = request.GET.get("tab", "revenue")
        if tab not in {"revenue", "products", "customers"}:
            tab = "revenue"
        active_period = request.GET.get("period", "month")
        today = timezone.now().date()
        date_from, date_to = AnalyticsService._get_period_bounds(active_period, today)
        previous_from, previous_to = AnalyticsService._get_previous_period(date_from, date_to)

        if tab == "products":
            report_payload = AnalyticsService._get_products_report_context(date_from, date_to)
        elif tab == "customers":
            report_payload = AnalyticsService._get_customers_report_context(date_from, date_to)
        else:
            report_payload = AnalyticsService._get_revenue_report_context(
                date_from, date_to, previous_from, previous_to
            )

        return {
            "active_tab": tab,
            "active_period": active_period,
            "report_title": str(_("Reports")),
            "period_label": str(
                _("Selected period: %(start)s - %(end)s")
                % {"start": date_from.strftime("%d.%m.%Y"), "end": date_to.strftime("%d.%m.%Y")}
            ),
            "report_tabs": [
                {"key": item["key"], "label": str(_(item["label"])), "icon": item["icon"]}
                for item in AnalyticsService.REPORT_TABS
            ],
            "period_options": [
                {"key": item["key"], "label": str(_(item["label"]))} for item in AnalyticsService.PERIOD_OPTIONS
            ],
            **report_payload,
        }


# --- Register Providers ---


@DashboardSelector.extend(cache_key="analytics_kpis", cache_ttl=0)
def provide_analytics_kpis(request: Any) -> Any:
    return AnalyticsService.get_kpi_metrics()


@DashboardSelector.extend(cache_key="analytics_charts", cache_ttl=0)
def provide_analytics_charts(request: Any) -> Any:
    return AnalyticsService.get_chart_data()


@DashboardSelector.extend(cache_key="analytics_lists", cache_ttl=0)
def provide_analytics_lists(request: Any) -> Any:
    return AnalyticsService.get_top_lists()
