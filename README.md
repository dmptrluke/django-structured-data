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
Define a `structured_data` property on your models.
```python
    @property
    def structured_data(self):
        return {
            '@type': 'BlogPosting',
            'title': self.title,
        }

```

### In templates
Use the `json_ld_for` template tag to render your structured data as JSON-LD.
```djangotemplate
{% json_ld_for post %}
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