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


class Category(
    TimestampMixin,
    ActiveMixin,
    SlugMixin,
    SeoMixin,
    OrderableMixin,
    models.Model,
):
    """Product Category Model."""

    name = models.CharField(_("Name"), max_length=150)
    is_featured = models.BooleanField(default=False, help_text="Show on the home page Bento grid")
    image = models.ImageField(_("Image"), upload_to="categories/", blank=True, null=True)
    description = models.TextField(_("Description"), blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent Category"),
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering: typing.ClassVar[list[str]] = ["order", "name"]

    def __str__(self) -> str:
        return self.name
