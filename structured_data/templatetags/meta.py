from django import template

from ..util import build_meta_tags, sub_defaults

register = template.Library()


@register.simple_tag()
def meta_for(obj):
    if hasattr(obj, 'structured_data'):
        data = sub_defaults(obj.structured_data)
        properties = {}

        # parse a description from the JSON-LD
        if 'description' in data:
            properties['description'] = data['description']

        return build_meta_tags(properties)
    else:
        return ""
