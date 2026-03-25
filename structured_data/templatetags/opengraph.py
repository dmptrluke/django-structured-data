from django import template
from django.conf import settings

from ..util import ARTICLE_TYPES, build_og_tags, resolve_structured_data

register = template.Library()


@register.simple_tag()
def og_for(obj):  # noqa: C901
    data = resolve_structured_data(obj)
    if data is not None:
        schema_type = data.get('@type')
        properties = []

        if 'name' in data:
            properties.append(('og:title', data['name']))

        if 'description' in data:
            properties.append(('og:description', data['description']))

        if 'image' in data:
            image = data['image']
            if isinstance(image, dict):
                properties.append(('og:image', image['url']))
                if 'width' in image and 'height' in image:
                    properties.append(('og:image:width', image['width']))
                    properties.append(('og:image:height', image['height']))
                if 'caption' in image:
                    properties.append(('og:image:alt', image['caption']))
            else:
                properties.append(('og:image', image))

        if 'url' in data:
            properties.append(('og:url', data['url']))

        if schema_type in ARTICLE_TYPES:
            properties.append(('og:type', 'article'))

            if 'headline' in data:
                properties.append(('og:title', data['headline']))
            if 'datePublished' in data:
                properties.append(('article:published_time', data['datePublished']))
            if 'dateModified' in data:
                properties.append(('article:modified_time', data['dateModified']))
            if 'author' in data:
                author = data['author']
                if isinstance(author, dict) and 'url' in author:
                    properties.append(('article:author', author['url']))
                elif isinstance(author, str):
                    properties.append(('article:author', author))
            if 'articleSection' in data:
                properties.append(('article:section', data['articleSection']))
            if 'keywords' in data and isinstance(data['keywords'], list):
                for keyword in data['keywords']:
                    properties.append(('article:tag', keyword))

        else:
            properties.append(('og:type', 'website'))

        return build_og_tags(properties)
    else:
        return ''


@register.simple_tag()
def og_sitewide():
    properties = getattr(settings, 'STRUCTURED_DATA_SITEWIDE_OG', {})
    if callable(properties):
        properties = properties()
    return build_og_tags(list(properties.items()))
