import typing
from typing import Any

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Order, OrderItem


class OrderItemInline(TabularInline[OrderItem, Order]):  # type: ignore[misc]
    model = OrderItem
    extra = 0
    readonly_fields = ("price",)


@admin.register(Order)
class OrderAdmin(ModelAdmin[Order]):  # type: ignore[misc]
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "contact_phone", "shipping_address")
    inlines: typing.ClassVar[list[type[TabularInline[Any, Any]]]] = [OrderItemInline]
