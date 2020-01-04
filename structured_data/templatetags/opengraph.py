from django import template

from ..util import sub_defaults, build_tags

register = template.Library()


@register.simple_tag()
def og_for(obj):
    if hasattr(obj, 'structured_data'):
        data = sub_defaults(obj.structured_data)
        properties = {}

        # parse a name from the JSON-LD
        if 'name' in data:
            properties['og:title'] = data['name']

        # parse a description from the JSON-LD
        if 'description' in data:
            properties['og:description'] = data['description']

        # parse an image from the JSON-LD
        if 'image' in data:
            properties['og:image'] = data['image']

        # parse a URL from the JSON-LD
        if 'url' in data:
            properties['og:url'] = data['url']

        # special cased actions for articles
        if data['@type'] in ("BlogPosting", "Article", "NewsArticle"):
            properties['og:type'] = 'article'

            if 'headline' in data:
                properties['og:title'] = data['headline']
            if 'datePublished' in data:
                properties['article:published_time'] = data['datePublished']
            if 'dateModified' in data:
                properties['article:modified_time'] = data['dateModified']

        return build_tags(properties)
    else:
        return ""
