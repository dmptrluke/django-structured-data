# Django Structured Data  [![PyPI](https://img.shields.io/pypi/v/django-structured-data)](https://pypi.org/project/django-structured-data/)
A template tag to assist in adding structured data to views and models.

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
Define a `structured_data` property on your models. This is written in a standard JSON-LD format. Included
 below is a complicated example.
```python
    @property
    def structured_data(self):
        url = SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'BlogPosting',
            'headline': self.title,
            'author': {
                '@type': 'Person',
                'name': self.author
            },
            'datePublished': self.created.strftime('%Y-%m-%d'),
            'dateModified': self.modified.strftime('%Y-%m-%d'),
            'url': url,
            'mainEntityOfPage': {
                '@type': 'WebPage',
                '@id': url
            },
        }
        if self.image:
            data['image'] = SITE_URL + self.image.url

        return data

```

### In templates
Use the `json_ld_for` template tag to render your structured data as JSON-LD.
```djangotemplate
{% load jsonld %}
{% json_ld_for post %}
```

A second template tag, `og_for`, is also included. This attempts to translate your JSON-LD 
data to Open Graph tags that can be read by Facebook, Twitter, Telegram 
and more.
 ```djangotemplate
{% load opengraph %}
{% og_for post %}
```

## License

This software is released under the MIT license.
```
Copyright (c) 2019 Luke Rogers

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