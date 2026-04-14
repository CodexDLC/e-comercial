from typing import ClassVar

from codex_django.system.mixins import AbstractUserProfile
from django.db import models


class UserProfile(AbstractUserProfile):
    phone_number = models.CharField("Контактный телефон", max_length=50, blank=True)
    shipping_address = models.TextField("Адрес доставки по умолчанию", blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return self.get_full_name() or f"Profile #{self.pk}"
