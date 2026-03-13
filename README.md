# Django Structured Data  [![PyPI](https://img.shields.io/pypi/v/django-structured-data)](https://pypi.org/project/django-structured-data/)

Django template tags that turn a single JSON-LD dict into rich metadata: JSON-LD script blocks, Open Graph tags, HTML meta tags, and Twitter Cards.

## Install

1.  Add "structured_data" to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'structured_data',
]
```

## Quick Start

### Define structured data on a model

```python
@property
def structured_data(self):
    return {
        '@type': 'BlogPosting',
        'headline': self.title,
        'description': self.summary,
        'author': {'@type': 'Person', 'name': self.author.name},
        'datePublished': self.created,
        'url': SITE_URL + self.get_absolute_url(),
        'image': {
            'url': SITE_URL + self.image.url,
            'width': 1200,
            'height': 630,
        },
    }
```

### Render in templates

```djangotemplate
{% load jsonld opengraph meta twitter %}

{% json_ld_for post %}
{% og_for post %}
{% meta_for post %}
{% twitter_for post %}
```

All four tags accept either an object with a `structured_data` property or a plain dict.

## Features

- **[Template Tags](docs/template-tags.md)**: JSON-LD, Open Graph, HTML meta, and Twitter Card output with automatic property mapping and dict passthrough
- **[View Mixin](docs/view-mixin.md)**: `StructuredDataMixin` injects structured data into template context from any class-based view
- **[Sitewide Tags](docs/sitewide.md)**: Render sitewide metadata from Django settings

## License

This software is released under the MIT license.
```
Copyright (c) 2019-2026 Luke Rogers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
