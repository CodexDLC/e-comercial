from typing import Any

from core.sitemaps import BaseSitemap

# from .models import YourModel


class YourModelSitemap(BaseSitemap):
    """
    Example of a model-based sitemap.
    """

    changefreq = "weekly"
    priority = 0.7

    def items(self) -> list[Any]:
        # return YourModel.objects.filter(is_active=True)
        return []

    def lastmod(self, obj: Any) -> Any:
        # return obj.updated_at
        return None

    def location(self, obj: Any) -> str:
        # return reverse("your_model_detail", kwargs={"slug": obj.slug})
        return "/"
