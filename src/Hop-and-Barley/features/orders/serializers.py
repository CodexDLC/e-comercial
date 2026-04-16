from typing import Any

from rest_framework import serializers

from features.products.serializers import ProductSerializer

from .models.order import Order
from .models.order_item import OrderItem


class OrderItemSerializer(serializers.ModelSerializer[OrderItem]):
    product_details = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_details", "quantity", "price")
        read_only_fields = ("price",)


class OrderSerializer(serializers.ModelSerializer[Order]):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "total_price",
            "shipping_address",
            "contact_phone",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user", "status", "total_price")


class CartItemAddSerializer(serializers.Serializer[Any]):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)


class CartItemRemoveSerializer(serializers.Serializer[Any]):
    product_id = serializers.IntegerField()
