from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Review


@admin.register(Review)
class ReviewAdmin(ModelAdmin):  # type: ignore[misc]
    list_display = ("user", "product", "rating", "is_active", "created_at")
    list_filter = ("rating", "is_active", "created_at")
    search_fields = ("user__email", "product__name", "comment")
    autocomplete_fields = ("user", "product")
