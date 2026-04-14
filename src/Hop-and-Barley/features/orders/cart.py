from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from typing import Any

from django.conf import settings

from features.products.models import Product


class Cart:
    def __init__(self, session: Any) -> None:
        self.session = session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: dict[str, dict[str, Any]] = cart

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        # Ensure we don't exceed stock
        if self.cart[product_id]["quantity"] > product.stock:
            self.cart[product_id]["quantity"] = product.stock

        self.save()

    def save(self) -> None:
        # If session is a dictionary (for tests), it won't have .modified
        if hasattr(self.session, "modified"):
            self.session.modified = True

    def remove(self, product: Product) -> None:
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self) -> Iterator[dict[str, Any]]:
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            if "product" not in item:
                continue
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self) -> int:
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        return Decimal(sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values()))

    def clear(self) -> None:
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        self.save()
