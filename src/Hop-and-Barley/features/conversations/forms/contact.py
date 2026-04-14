from typing import Any, ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Message


class ContactForm(forms.ModelForm[Message]):
    class Meta:
        model = Message
        fields: ClassVar[list[str]] = ["sender_name", "sender_email", "sender_phone", "subject", "topic", "body"]
        labels: ClassVar[dict[str, Any]] = {
            "sender_name": _("Your Name"),
            "sender_email": _("Email Address"),
            "sender_phone": _("Phone Number"),
            "subject": _("Subject"),
            "topic": _("Inquiry Type"),
            "body": _("How can we help?"),
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "body": forms.Textarea(attrs={"rows": 5}),
            "sender_phone": forms.TextInput(attrs={"placeholder": _("+49 …")}),
        }
