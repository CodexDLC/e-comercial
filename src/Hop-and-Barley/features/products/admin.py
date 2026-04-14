import typing

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):  # type: ignore
    list_display = ("name", "parent", "is_active", "is_featured", "order")
    list_filter = ("is_active", "is_featured")
    search_fields = ("name", "slug", "description")
    prepopulated_fields: typing.ClassVar[dict[str, tuple[str]]] = {"slug": ("name",)}
    autocomplete_fields: typing.ClassVar[tuple[str]] = ("parent",)


@admin.register(Product)
class ProductAdmin(ModelAdmin):  # type: ignore
    list_display = ("name", "category", "price", "stock", "is_active", "order")
    list_filter = ("is_active", "category")
    search_fields = ("name", "slug", "description")
    prepopulated_fields: typing.ClassVar[dict[str, tuple[str]]] = {"slug": ("name",)}
    autocomplete_fields: typing.ClassVar[tuple[str]] = ("category",)
