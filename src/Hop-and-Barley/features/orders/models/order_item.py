from django.db import models
from django.utils.translation import gettext_lazy as _

from features.products.models import Product

from .order import Order


class OrderItem(models.Model):
    """Order Item Model."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Заказ"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name=_("Товар"),
    )
    quantity = models.PositiveIntegerField(_("Количество"), default=1)
    price = models.DecimalField(_("Цена за единицу (замороженная)"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказа")

    def __str__(self) -> str:
        if self.product:
            return f"{self.quantity} x {self.product.name}"
        return f"{self.quantity} x удаленный товар"
