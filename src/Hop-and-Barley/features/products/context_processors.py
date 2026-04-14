from typing import Any

from django.http import HttpRequest

from features.products.models import Category


def categories(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor to provide active categories to all templates.
    """
    return {"all_categories": Category.objects.filter(is_active=True).order_by("order")}
