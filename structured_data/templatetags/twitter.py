from django import template

from ..util import LARGE_IMAGE_TYPES, build_meta_tags, extract_author_name

register = template.Library()


@register.simple_tag()
def twitter_for(obj):
    if hasattr(obj, 'structured_data'):
        data = obj.structured_data
        properties = {}

        if data.get('@type') in LARGE_IMAGE_TYPES:
            properties['twitter:card'] = 'summary_large_image'
        else:
            properties['twitter:card'] = 'summary'

        if 'image' in data:
            image = data['image']
            if isinstance(image, dict):
                properties['twitter:image'] = image['url']
                if 'caption' in image:
                    properties['twitter:image:alt'] = image['caption']
            else:
                properties['twitter:image'] = image

        if 'author' in data:
            name = extract_author_name(data['author'])
            if name:
                properties['twitter:creator'] = name

        return build_meta_tags(properties)
    else:
        return ''
