import typing

from codex_django.core.mixins.models import (
    ActiveMixin,
    OrderableMixin,
    SeoMixin,
    SlugMixin,
    TimestampMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from .category import Category


class Product(
    TimestampMixin,
    ActiveMixin,
    SlugMixin,
    SeoMixin,
    OrderableMixin,
    models.Model,
):
    """Product Model."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Категория"),
    )
    name = models.CharField(_("Название"), max_length=200)
    description = models.TextField(_("Описание"), blank=True)
    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_("Остаток на складе"), default=0)
    image = models.ImageField(_("Изображение товара"), upload_to="products/", blank=True, null=True)
    specifications = models.JSONField(_("Технические характеристики"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering: typing.ClassVar[list[str]] = ["order", "name"]

    def __str__(self) -> str:
        return self.name
