from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..util import json_encode, resolve_structured_data

register = template.Library()


@register.simple_tag()
def json_ld_for(obj):
    data = resolve_structured_data(obj)
    if data is None:
        return ''

    data = data.copy()
    if '@context' not in data:
        data['@context'] = 'https://schema.org'

    encoded = json_encode(data)
    return format_html('<script type="application/ld+json">{}</script>', mark_safe(encoded))


@register.simple_tag()
def json_ld_sitewide():
    data_list = getattr(settings, 'STRUCTURED_DATA_SITEWIDE', [])
    if callable(data_list):
        data_list = data_list()
    fragments = []
    for data in data_list:
        data = data.copy()
        if '@context' not in data:
            data['@context'] = 'https://schema.org'
        encoded = json_encode(data)
        fragments.append(format_html('<script type="application/ld+json">{}</script>', mark_safe(encoded)))
    return mark_safe('\n'.join(fragments))
