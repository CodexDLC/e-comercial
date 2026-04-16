from typing import TYPE_CHECKING, Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

if TYPE_CHECKING:
    from django.contrib.auth.models import User

from features.products.models import Product

from .models.order import Order
from .models.order_item import OrderItem
from .serializers import (
    CartItemAddSerializer,
    CartItemRemoveSerializer,
    OrderSerializer,
)
from .services.cart import CartService


class OrderViewSet(viewsets.ModelViewSet[Order]):
    """
    API endpoint for viewing and creating orders.
    """

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self) -> Any:
        user = cast("User", self.request.user)
        return Order.objects.filter(user=user)

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        user = cast("User", request.user)
        cart = CartService.get_cart(request)
        if not cart:
            return Response(
                {"detail": "Корзина пуста. Добавьте товары перед оформлением заказа."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save(user=user)
        total_price = 0

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total_price += price * quantity

        order.total_price = total_price
        order.save()

        CartService.clear(request)

        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)


class CartViewSet(viewsets.ViewSet):
    """
    API endpoint for managing the session-based shopping cart.
    """

    permission_classes = (AllowAny,)

    def list(self, request: Any) -> Response:
        cart = CartService.get_cart(request)
        return Response(cart)

    @action(detail=False, methods=["post"])
    def add(self, request: Any) -> Response:
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = CartService.add(request, **serializer.validated_data)
        return Response(cart)

    @action(detail=False, methods=["post"])
    def remove(self, request: Any) -> Response:
        serializer = CartItemRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = CartService.remove(request, **serializer.validated_data)
        return Response(cart)
