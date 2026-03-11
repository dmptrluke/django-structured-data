from django import template

from ..util import ARTICLE_TYPES, build_og_tags

register = template.Library()


@register.simple_tag()
def og_for(obj):
    if hasattr(obj, 'structured_data'):
        data = obj.structured_data
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
