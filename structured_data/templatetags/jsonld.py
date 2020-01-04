import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

_json_script_escapes = {
    ord('>'): '\\u003E',
    ord('<'): '\\u003C',
    ord('&'): '\\u0026',
}


@register.simple_tag()
def json_ld_for(obj):
    if hasattr(obj, 'structured_data'):
        data = obj.structured_data

        if '@context' not in data:
            data['@context'] = "https://schema.org"

        encoded = json.dumps(data, cls=DjangoJSONEncoder).translate(_json_script_escapes)
        return format_html(
            '<script type="application/ld+json">{}</script>',
            mark_safe(encoded)
        )
