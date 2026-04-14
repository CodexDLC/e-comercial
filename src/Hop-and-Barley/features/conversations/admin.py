from typing import Any, ClassVar

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import Message, MessageReply


class MessageReplyInline(TabularInline[MessageReply, Message]):  # type: ignore[misc]
    model = MessageReply
    extra = 0
    fields = ("sent_by", "body", "is_inbound", "sent_at")
    readonly_fields = ("sent_at",)


@admin.register(Message)
class MessageAdmin(ModelAdmin[Message]):  # type: ignore[misc]
    list_display = ("sender_name", "sender_email", "topic", "status", "source", "channel", "created_at")
    list_filter = ("status", "topic", "source", "channel")
    search_fields = ("sender_name", "sender_email", "sender_phone", "subject", "body")
    readonly_fields = ("thread_key", "created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines: ClassVar[list[type[TabularInline[Any, Any]]]] = [MessageReplyInline]

    fieldsets: ClassVar[list[tuple[str | None, dict[str, Any]]]] = [
        (str(_("Sender")), {"fields": ["sender_name", "sender_email", "sender_phone"]}),
        (str(_("Content")), {"fields": ["subject", "body"]}),
        (str(_("Classification")), {"fields": ["topic", "status", "source", "channel"]}),
        (str(_("Meta")), {"fields": ["thread_key", "created_at", "updated_at"], "classes": ["collapse"]}),
    ]
