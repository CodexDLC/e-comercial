from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import transaction

from features.orders.models.order import Order
from features.orders.models.order_item import OrderItem

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class OrderService:
    """Core business logic for orders."""

    @classmethod
    def update_status(cls, order_id: uuid.UUID | str, new_status: str) -> None:
        Order.objects.filter(id=order_id).update(status=new_status)

    @classmethod
    @transaction.atomic
    def create_order(
        cls,
        user: AbstractBaseUser | AnonymousUser,
        cart: Any,
        full_name: str,
        email: str,
        phone: str,
        address: str,
    ) -> Order:
        """
        Creates an order from cart items and updates product stock.
        """
        # Create Order
        order_user = cast("User | None", user if user.is_authenticated else None)
        order = Order.objects.create(
            user=order_user,
            shipping_address=f"{full_name}\n{email}\n{address}",
            contact_phone=str(phone),
            total_price=cart.get_total_price(),
        )

        # Create OrderItems and Update Stock
        for item in cart:
            OrderItem.objects.create(
                order=order, product=item["product"], price=item["price"], quantity=item["quantity"]
            )
            # Update stock
            product = item["product"]
            product.stock -= item["quantity"]
            product.save(update_fields=["stock"])

        # Clear cart
        cart.clear()

        return order
