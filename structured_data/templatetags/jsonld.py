import json

from django import template
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe

DEFAULT_STRUCTURED_DATA = getattr(settings, 'DEFAULT_STRUCTURED_DATA', {})

register = template.Library()

_json_script_escapes = {
    ord('>'): '\\u003E',
    ord('<'): '\\u003C',
    ord('&'): '\\u0026',
}


@register.simple_tag()
def json_ld_for(obj):
    if hasattr(obj, 'structured_data'):
        raw_data = obj.structured_data
        data = {}

        # if value is None, pull value from DEFAULT_STRUCTURED_DATA by key
        for key, value in raw_data.items():
            if value is None:
                data[key] = DEFAULT_STRUCTURED_DATA[key]
            else:
                data[key] = value

        if '@context' not in data:
            data['@context'] = "https://schema.org"

        encoded = json.dumps(data, cls=DjangoJSONEncoder).translate(_json_script_escapes)
        return format_html(
            '<script type="application/ld+json">{}</script>',
            mark_safe(encoded)
        )
