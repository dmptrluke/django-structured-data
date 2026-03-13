# View Mixin

`StructuredDataMixin` injects structured data into template context from any class-based view. This is useful for pages that need metadata but don't have a single model object.

## Usage

```python
from structured_data.views import StructuredDataMixin

class EventListView(StructuredDataMixin, ListView):
    def get_structured_data(self):
        return {
            '@type': 'CollectionPage',
            'name': 'Events',
            'description': 'Upcoming events',
            'url': self.request.build_absolute_uri(),
        }
```

The returned dict is added to the template context as `structured_data`, which can be passed to any template tag:

```djangotemplate
{% load jsonld opengraph meta twitter %}

{% json_ld_for structured_data %}
{% og_for structured_data %}
{% meta_for structured_data %}
{% twitter_for structured_data %}
```
