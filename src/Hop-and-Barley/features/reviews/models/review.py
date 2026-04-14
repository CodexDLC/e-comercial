import typing

from codex_django.core.mixins.models import ActiveMixin, TimestampMixin
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from features.products.models import Product


class Review(TimestampMixin, ActiveMixin, models.Model):
    """Product Review Model."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Товар"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Пользователь"),
    )
    rating = models.PositiveSmallIntegerField(_("Оценка (1-5)"))
    comment = models.TextField(_("Комментарий"))

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering: typing.ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return f"Отзыв на {self.product.name} от {self.user.username}"
