# Django Structured Data  [![PyPI](https://img.shields.io/pypi/v/django-structured-data)](https://pypi.org/project/django-structured-data/)
Template tags to assist in adding structured metadata to views and models.

## Install

1.  Add "structured_data" to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'structured_data',
]
```

## Use

### In models
Define a `structured_data` property on your models. This is written in a standard JSON-LD format. You can add as much or as little detail as you like - only data that exists will be mapped. Below is a very detailed example.
```python
    @property
    def structured_data(self):
        url = SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'BlogPosting',
            'headline': self.title,
            'description': self.summary,
            'author': {
                '@type': 'Person',
                'name': self.author.name,
                'url': self.author.get_absolute_url(),
            },
            'datePublished': self.created,
            'dateModified': self.modified,
            'url': url,
            'inLanguage': 'en-US',
            'keywords': ['python', 'django'],
            'articleSection': 'Technology',
            'publisher': {
                '@type': 'Organization',
                'name': 'My Site',
            },
            'image': {
                'url': SITE_URL + self.image.url,
                'width': 1200,
                'height': 630,
                'caption': 'A description of the image',
            },
        }
        return data
```

### In templates

#### JSON-LD
Use the `json_ld_for` template tag to render your structured data as JSON-LD.
```djangotemplate
{% load jsonld %}
{% json_ld_for post %}
```

#### Open Graph
The `og_for` tag translates your JSON-LD data to Open Graph meta tags for Facebook, Telegram, and other platforms.
```djangotemplate
{% load opengraph %}
{% og_for post %}
```

The following JSON-LD properties are mapped:

| JSON-LD | Open Graph |
|---|---|
| `name` | `og:title` |
| `description` | `og:description` |
| `url` | `og:url` |
| `image` (string or dict) | `og:image`, `og:image:width`, `og:image:height` |
| `image.caption` | `og:image:alt` |

For `Article`, `BlogPosting`, and `NewsArticle` types, additional mappings apply:

| JSON-LD | Open Graph |
|---|---|
| `headline` | `og:title` (overrides `name`) |
| `datePublished` | `article:published_time` |
| `dateModified` | `article:modified_time` |
| `author` (string or `.url`) | `article:author` |
| `articleSection` | `article:section` |
| `keywords` (list) | `article:tag` (one per keyword) |

All other types (including `Event` and its subtypes) receive `og:type = website`.

#### HTML Meta Tags
The `meta_for` tag extracts standard HTML meta tags from your JSON-LD data.
```djangotemplate
{% load meta %}
{% meta_for post %}
```

| JSON-LD | Meta Tag |
|---|---|
| `description` | `<meta name="description">` |
| `author` (string or `.name`) | `<meta name="author">` |
| `keywords` (list or string) | `<meta name="keywords">` |
| `location` (string or `.name`) | `<meta name="location">` |

#### Twitter Cards
The `twitter_for` tag generates Twitter Card meta tags.
```djangotemplate
{% load twitter %}
{% twitter_for post %}
```

| JSON-LD | Twitter Tag |
|---|---|
| `@type` | `twitter:card` (`summary_large_image` for articles, events, and recipes; `summary` otherwise) |
| `image.caption` | `twitter:image:alt` |
| `author` (string or `.name`) | `twitter:creator` |

Twitter falls back to Open Graph tags for title, description, and image, so `og_for` should be used alongside `twitter_for`.

#### Global tags
Some Open Graph properties like `og:site_name` and `og:locale` are site-wide and not specific to any one object. Add these directly in your base template:
```djangotemplate
<meta property="og:site_name" content="My Site" />
<meta property="og:locale" content="en_US" />
```

If you want a site-wide JSON-LD identity, add an `Organization` block in your base template with an `@id` so individual pages can reference it:
```djangotemplate
<script type="application/ld+json">
{"@context": "https://schema.org", "@type": "Organization", "@id": "https://example.com/#organization", "name": "My Site", "url": "https://example.com"}
</script>
```

Then reference it from your model's `structured_data` using the same `@id`:
```python
'publisher': {'@id': 'https://example.com/#organization'}
```

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
