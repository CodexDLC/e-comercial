from __future__ import annotations

from features.products.models import Product


class ProductService:
    """Core business logic for products (FeatureService)."""

    @classmethod
    def update_stock(cls, product_id: int, quantity: int) -> None:
        product = Product.objects.get(pk=product_id)
        product.stock = quantity
        product.save()

    @classmethod
    def toggle_active_status(cls, product_id: int) -> bool:
        product = Product.objects.get(pk=product_id)
        product.is_active = not product.is_active
        product.save()
        return product.is_active
