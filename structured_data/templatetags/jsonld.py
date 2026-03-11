from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..util import json_encode

register = template.Library()


@register.simple_tag()
def json_ld_for(obj):
    if hasattr(obj, 'structured_data'):
        data = obj.structured_data.copy()

        if '@context' not in data:
            data['@context'] = 'https://schema.org'

        encoded = json_encode(data)
        return format_html('<script type="application/ld+json">{}</script>', mark_safe(encoded))
    else:
        return ''
