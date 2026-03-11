from django import template

from ..util import build_meta_tags, extract_author_name, extract_location_name

register = template.Library()


@register.simple_tag()
def meta_for(obj):
    if hasattr(obj, 'structured_data'):
        data = obj.structured_data
        properties = {}

        if 'description' in data:
            properties['description'] = data['description']

        if 'author' in data:
            name = extract_author_name(data['author'])
            if name:
                properties['author'] = name

        if 'keywords' in data:
            kw = data['keywords']
            if isinstance(kw, list):
                properties['keywords'] = ', '.join(kw)
            elif isinstance(kw, str):
                properties['keywords'] = kw

        if 'location' in data:
            loc = extract_location_name(data['location'])
            if loc:
                properties['location'] = loc

        return build_meta_tags(properties)
    else:
        return ''
