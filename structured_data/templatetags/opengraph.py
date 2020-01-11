from django import template

from ..util import build_og_tags, sub_defaults

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
            image = data['image']
            if isinstance(image, dict):
                properties['og:image'] = image['url']
                if 'width' in image and 'height' in image:
                    properties['og:image:width'] = image['width']
                    properties['og:image:height'] = image['height']
            else:
                properties['og:image'] = image

        # parse a URL from the JSON-LD
        if 'url' in data:
            properties['og:url'] = data['url']

        # special cased actions for websites
        if data['@type'] == "WebSite":
            properties['og:type'] = 'website'

        # special cased actions for articles
        if data['@type'] in ("BlogPosting", "Article", "NewsArticle"):
            properties['og:type'] = 'article'

            if 'headline' in data:
                properties['og:title'] = data['headline']
            if 'datePublished' in data:
                properties['article:published_time'] = data['datePublished']
            if 'dateModified' in data:
                properties['article:modified_time'] = data['dateModified']

        return build_og_tags(properties)
    else:
        return ""
