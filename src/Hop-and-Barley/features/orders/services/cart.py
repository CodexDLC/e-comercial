from __future__ import annotations

from typing import Any, cast

from django.http import HttpRequest


class CartService:
    @staticmethod
    def get_cart(request: HttpRequest) -> dict[str, Any]:
        return cast(dict[str, Any], request.session.get("cart", {}))

    @staticmethod
    def add(request: HttpRequest, product_id: str | int, quantity: int = 1) -> dict[str, Any]:
        cart = cast(dict[str, Any], request.session.get("cart", {}))
        cart[str(product_id)] = cart.get(str(product_id), 0) + int(quantity)
        request.session["cart"] = cart
        return cart

    @staticmethod
    def remove(request: HttpRequest, product_id: str | int) -> dict[str, Any]:
        cart = cast(dict[str, Any], request.session.get("cart", {}))
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session["cart"] = cart
        return cart

    @staticmethod
    def clear(request: HttpRequest) -> None:
        request.session.pop("cart", None)
        request.session.modified = True
