from typing import Any

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from core.sitemaps import sitemaps

# Error Handlers
handler404 = "system.views.errors.handler404"
handler500 = "system.views.errors.handler500"
handler403 = "system.views.errors.handler403"
handler400 = "system.views.errors.handler400"

# Non-prefixed patterns (API, technical files)
urlpatterns: list[Any] = [
    path("api/", include("core.api_urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("llms_de.txt", TemplateView.as_view(template_name="llms_de.txt", content_type="text/plain")),
    path("llms_en.txt", TemplateView.as_view(template_name="llms_en.txt", content_type="text/plain")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("cabinet.auth_urls")),
    path("cabinet/", include("cabinet.urls")),
    path("system/", include("system.urls")),
    path("showcase/", include("codex_django.showcase.urls")),
    path("conversations/", include("features.conversations.urls")),
    path("catalog/", include("features.products.urls", namespace="products")),
    path("orders/", include("features.orders.urls", namespace="orders")),
    path("reviews/", include("features.reviews.urls", namespace="reviews")),
    path("", include("features.main.urls", namespace="main")),
    prefix_default_language=True,
)
