# Sitewide Tags

Two template tags render site-level metadata from Django settings: `json_ld_sitewide` for JSON-LD blocks (Organization, WebSite, etc.) and `og_sitewide` for Open Graph properties like `og:site_name` and `og:locale`.

## Sitewide JSON-LD

Add `STRUCTURED_DATA_SITEWIDE` to your Django settings:

```python
STRUCTURED_DATA_SITEWIDE = [
    {
        '@type': 'Organization',
        '@id': 'https://example.com/#organization',
        'name': 'Example',
        'url': 'https://example.com',
        'logo': {
            '@type': 'ImageObject',
            'url': 'https://example.com/logo.png',
            'width': 90,
            'height': 90,
        },
    },
]
```

```djangotemplate
{% load jsonld %}
{% json_ld_sitewide %}
```

Each dict in the list gets its own `<script type="application/ld+json">` block. `@context` is added automatically if missing.

### Callable support

Both settings accept a callable instead of a static value. The callable is invoked at template render time, allowing dynamic content (e.g. from a database model):

```python
def get_sitewide_jsonld():
    from myapp.models import SiteSettings
    s = SiteSettings.objects.get()
    return [
        {
            '@type': 'Organization',
            'name': s.org_name,
            'url': 'https://example.com',
        },
    ]

STRUCTURED_DATA_SITEWIDE = get_sitewide_jsonld
```

For request-dependent data, use the [View Mixin](view-mixin.md) instead.

Individual model metadata can reference sitewide entities using `@id`:

```python
'publisher': {'@id': 'https://example.com/#organization'}
```

## Sitewide Open Graph

Add `STRUCTURED_DATA_SITEWIDE_OG` to your Django settings:

```python
STRUCTURED_DATA_SITEWIDE_OG = {
    'og:site_name': 'My Site',
    'og:locale': 'en_US',
}
```

```djangotemplate
{% load opengraph %}
{% og_sitewide %}
```

Each key/value pair renders as a `<meta property="..." content="..." />` tag.
