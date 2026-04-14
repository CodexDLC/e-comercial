from typing import Any
from rest_framework import viewsets, permissions
from rest_framework.serializers import BaseSerializer
from rest_framework.request import Request
from rest_framework.permissions import BasePermission

from .models.review import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet[Review]):
    """
    API endpoint for viewing and creating reviews.
    """
    serializer_class = ReviewSerializer
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self) -> Any:
        queryset = Review.objects.filter(is_active=True)
        product_id = self.request.query_params.get('product_id')
        
        # Alternatively, we can use URL kwargs if building nested routers, 
        # but query parameters or standard viewset filtering works too.
        # The checklist says GET /api/reviews/{product_id}/ but standard DRF 
        # usually handles nested objects via dedicated routes or query_params.
        # Let's support both nested route lookup and query param.
        
        product_pk = self.kwargs.get('product_pk')
        if product_pk:
            queryset = queryset.filter(product_id=product_pk)
        elif product_id:
            queryset = queryset.filter(product_id=product_id)
            
        return queryset

    def get_permissions(self) -> list[BasePermission]:
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer: BaseSerializer[Review]) -> None:
        serializer.save(user=self.request.user)
