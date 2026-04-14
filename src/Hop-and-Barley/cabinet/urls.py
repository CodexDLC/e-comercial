from django.conf import settings
from django.urls import include, path

from .views.analytics import AnalyticsReportsView, analytics_dashboard_view
from .views.client import ClientAppointmentsView, ClientHomeView
from .views.conversations import (
    AllMessagesView,
    ComposeView,
    InboxBulkActionView,
    InboxView,
    ProcessedView,
    ThreadActionView,
    ThreadReplyActionView,
    ThreadView,
    manual_check_view,
)
from .views.orders import OrderDetailView, OrdersManagementView, OrderStatusUpdateView
from .views.products import (
    ProductCatalogListView,
    ProductCreateView,
    ProductUpdateView,
)
from .views.site_settings import site_settings_tab_view, site_settings_view
from .views.users import UserListView

app_name = "cabinet"

urlpatterns = [
    path("site/settings/", site_settings_view, name="site_settings"),
    path("site/settings/<str:tab_slug>/", site_settings_tab_view, name="site_settings_tab"),
    # Codex cabinet library: dashboard + generic routes
    path("", include("codex_django.cabinet.urls")),
    path("", include("cabinet.auth_urls")),
    path("my/", ClientHomeView.as_view(), name="client_home"),
    path("my/orders/", ClientAppointmentsView.as_view(), name="client_orders"),
    # Analytics
    path("analytics/", analytics_dashboard_view, name="analytics_dashboard"),
    path("analytics/reports/", AnalyticsReportsView.as_view(), name="analytics_reports"),
    # Conversations
    path("conversations/", InboxView.as_view(), name="conversations_inbox"),
    path("conversations/processed/", ProcessedView.as_view(), name="conversations_processed"),
    path("conversations/all/", AllMessagesView.as_view(), name="conversations_all"),
    path("conversations/compose/", ComposeView.as_view(), name="conversations_compose"),
    path("conversations/<int:pk>/", ThreadView.as_view(), name="conversations_thread"),
    path("conversations/<int:pk>/reply/", ThreadReplyActionView.as_view(), name="conversations_reply"),
    path("conversations/<int:pk>/action/<str:action>/", ThreadActionView.as_view(), name="conversations_action"),
    path("conversations/actions/bulk/", InboxBulkActionView.as_view(), name="conversations_bulk_action"),
    path("conversations/check-inbox/", manual_check_view, name="conversations_check_inbox"),
    # Users / Clients
    path("users/", UserListView.as_view(), name="users_list"),
    # Products
    path("products/", ProductCatalogListView.as_view(), name="product_catalog"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    # Orders
    path("orders/", OrdersManagementView.as_view(), name="orders_list"),
    path("orders/<uuid:pk>/", OrderDetailView.as_view(), name="orders_detail"),
    path("orders/<uuid:pk>/status/", OrderStatusUpdateView.as_view(), name="orders_status_update"),
]

if getattr(settings, "CODEX_ALLAUTH_ENABLED", False):
    urlpatterns.insert(2, path("", include("allauth.urls")))
