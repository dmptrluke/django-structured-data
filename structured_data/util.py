import json
from typing import Dict

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html_join

DEFAULT_STRUCTURED_DATA = getattr(settings, 'DEFAULT_STRUCTURED_DATA', {})

_json_script_escapes = {
    ord('>'): '\\u003E',
    ord('<'): '\\u003C',
    ord('&'): '\\u0026',
}


def json_encode(data: Dict) -> str:
    return json.dumps(data, cls=DjangoJSONEncoder).translate(_json_script_escapes)


def build_og_tags(properties: Dict[str, str]) -> str:
    return format_html_join('\n', '<meta property="{}" content="{}" />', properties.items())


def build_meta_tags(properties: Dict[str, str]) -> str:
    return format_html_join('\n', '<meta name="{}" content="{}" />', properties.items())


def sub_defaults(data: Dict) -> Dict:
    data_out = {}
    # if value is None, pull value from DEFAULT_STRUCTURED_DATA by key
    for key, value in data.items():
        if value is None:
            data_out[key] = DEFAULT_STRUCTURED_DATA[key]
        else:
            data_out[key] = value

    return data_out
