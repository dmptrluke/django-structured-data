# Template Tags

Four template tags render structured metadata from a JSON-LD dict. Define your data once and each tag pulls out what it needs.

All tags accept either a model object with a `structured_data` property, or a plain dict of JSON-LD formatted data passed directly through the template context. If the input is neither, the tag returns an empty string.

## JSON-LD

```djangotemplate
{% load jsonld %}
{% json_ld_for post %}
```

Renders a `<script type="application/ld+json">` block. `@context` is set to `https://schema.org` automatically if not present.

## Open Graph

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

## HTML Meta Tags

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

## Twitter Cards

```djangotemplate
{% load twitter %}
{% twitter_for post %}
```

| JSON-LD | Twitter Tag |
|---|---|
| `@type` | `twitter:card` (`summary_large_image` for articles, events, and recipes; `summary` otherwise) |
| `image` (string or dict) | `twitter:image` |
| `image.caption` | `twitter:image:alt` |
| `author` (string or `.name`) | `twitter:creator` |

Twitter falls back to Open Graph tags for title and description, so `og_for` should be used alongside `twitter_for`.
