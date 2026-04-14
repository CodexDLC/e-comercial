import typing
from typing import Any

from codex_django.core.mixins.models import TimestampMixin, UUIDMixin
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Order(TimestampMixin, UUIDMixin, models.Model):
    """Order Model."""

    STATUS_CHOICES: typing.ClassVar[list[tuple[str, Any]]] = [
        ("pending", _("В ожидании")),  # noqa: RUF001
        ("processing", _("Оформляется")),
        ("shipped", _("Отправлен")),
        ("delivered", _("Доставлен")),
        ("cancelled", _("Отменен")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Пользователь"),
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    total_price = models.DecimalField(_("Общая сумма"), max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.TextField(_("Адрес доставки"))
    contact_phone = models.CharField(_("Контактный телефон"), max_length=50)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering: typing.ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return f"Заказ {self.id} - {self.get_status_display()}"
