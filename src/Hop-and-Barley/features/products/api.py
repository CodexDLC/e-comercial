from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models.product import Product
from .serializers import ProductSerializer


class ProductFilter(filters.FilterSet):  # type: ignore[misc]
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = filters.CharFilter(field_name="category__slug")

    class Meta:
        model = Product
        fields = ("category", "price_min", "price_max")


class ProductViewSet(viewsets.ReadOnlyModelViewSet[Product]):
    """
    API endpoint that allows products to be viewed.
    """

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = "slug"
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ("name", "description")
    ordering_fields = ("price", "created_at")
    ordering = ("-created_at",)
