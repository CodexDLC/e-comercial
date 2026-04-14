from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from features.products.api import ProductViewSet
from features.orders.api import OrderViewSet, CartViewSet
from features.reviews.api import ReviewViewSet

from system.views.health import health_check

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),
        path('health/', health_check, name='api_health'),
        
        # JWT Auth
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
        # OpenAPI Swagger Docs
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ])),
]
