from codex_django.cabinet.templatetags.cabinet_tags import jsonify
from django import template

register = template.Library()
register.filter("jsonify", jsonify)


@register.filter
def get_item(mapping: object, key: str) -> object:
    if isinstance(mapping, dict):
        return mapping.get(key, "")
    return ""
