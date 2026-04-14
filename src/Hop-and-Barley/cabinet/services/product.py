from __future__ import annotations

from typing import Any

from codex_django.cabinet.types import MetricWidgetData
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from features.products.models import Category, Product


class ProductCabinetService:
    """Service for transforming product data into Cabinet UI types."""

    @classmethod
    def get_catalog_context(cls, request: HttpRequest) -> dict[str, Any]:
        category_slug = request.GET.get("category")
        queryset = Product.objects.all()

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        categories = Category.objects.filter(is_active=True).order_by("order")

        return {
            "products": queryset,
            "categories": categories,
            "active_category": category_slug,
            "header_title": str(_("Catalog")),
            "header_subtitle": str(_("Product Management")),
        }

    @classmethod
    def get_dashboard_metrics(cls) -> list[MetricWidgetData]:
        total_count = Product.objects.count()
        out_of_stock = Product.objects.filter(stock__lte=0).count()

        # MetricWidgetData doesn't take 'color' directly in its constructor
        return [
            MetricWidgetData(
                label=str(_("Total Products")),
                value=str(total_count),
                icon="bi-box-seam",
            ),
            MetricWidgetData(
                label=str(_("Out of Stock")),
                value=str(out_of_stock),
                icon="bi-exclamation-triangle",
            ),
        ]
