import datetime

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.views.generic import TemplateView

from ..templatetags.jsonld import json_ld_for, json_ld_sitewide
from ..templatetags.meta import meta_for
from ..templatetags.opengraph import og_for, og_sitewide
from ..templatetags.twitter import twitter_for
from ..util import (
    build_meta_tags,
    build_og_tags,
    extract_author_name,
    extract_location_name,
    format_time,
    json_encode,
    resolve_structured_data,
)
from ..views import StructuredDataMixin


class FormatTimeTests(SimpleTestCase):
    # datetime objects produce ISO 8601 with T separator
    def test_datetime(self):
        dt = datetime.datetime(2024, 1, 15, 10, 30, 0)
        assert format_time(dt) == '2024-01-15T10:30:00'

    # date objects produce YYYY-MM-DD
    def test_date(self):
        d = datetime.date(2024, 1, 15)
        assert format_time(d) == '2024-01-15'

    # time objects produce HH:MM:SS
    def test_time(self):
        t = datetime.time(10, 30, 0)
        assert format_time(t) == '10:30:00'

    # non-datetime values pass through unchanged
    def test_passthrough(self):
        assert format_time('hello') == 'hello'
        assert format_time(42) == 42


class BuildOgTagsTests(SimpleTestCase):
    # datetime values in OG tags are formatted as ISO 8601
    def test_datetime_in_og_tags(self):
        props = [('article:published_time', datetime.datetime(2024, 6, 15, 14, 30))]
        result = str(build_og_tags(props))
        assert '2024-06-15T14:30:00' in result

    # date values in OG tags are formatted as YYYY-MM-DD
    def test_date_in_og_tags(self):
        props = [('article:published_time', datetime.date(2024, 6, 15))]
        result = str(build_og_tags(props))
        assert '2024-06-15' in result

    # repeated properties render as separate meta tags
    def test_repeated_properties(self):
        props = [
            ('article:tag', 'python'),
            ('article:tag', 'django'),
            ('article:tag', 'web'),
        ]
        result = str(build_og_tags(props))
        assert result.count('article:tag') == 3
        assert 'python' in result
        assert 'django' in result
        assert 'web' in result


class BuildMetaTagsTests(SimpleTestCase):
    # datetime values in meta tags are formatted as ISO 8601
    def test_datetime_in_meta_tags(self):
        props = {'date': datetime.datetime(2024, 6, 15, 14, 30)}
        result = str(build_meta_tags(props))
        assert '2024-06-15T14:30:00' in result


class JsonEncodeTests(SimpleTestCase):
    # XSS-sensitive characters are escaped
    def test_escapes_angle_brackets_and_ampersand(self):
        result = json_encode({'name': '<script>alert("xss")</script>', 'note': 'a&b'})
        assert '<' not in result
        assert '>' not in result
        assert '&' not in result
        assert '\\u003C' in result
        assert '\\u003E' in result
        assert '\\u0026' in result


class _FakeObj:
    def __init__(self, data):
        self.structured_data = data


class JsonLdForTests(SimpleTestCase):
    # adds @context automatically
    def test_adds_context(self):
        obj = _FakeObj({'@type': 'WebSite', 'name': 'Test'})
        result = str(json_ld_for(obj))
        assert 'https://schema.org' in result

    # preserves existing @context
    def test_preserves_existing_context(self):
        obj = _FakeObj({'@context': 'https://custom.org', '@type': 'WebSite', 'name': 'Test'})
        result = str(json_ld_for(obj))
        assert 'https://custom.org' in result
        assert result.count('@context') == 1

    # wraps output in script tag
    def test_script_tag(self):
        obj = _FakeObj({'@type': 'WebSite', 'name': 'Test'})
        result = str(json_ld_for(obj))
        assert result.startswith('<script type="application/ld+json">')
        assert result.endswith('</script>')

    # no output for objects without structured_data
    def test_no_structured_data(self):
        result = str(json_ld_for(object()))
        assert result == ''


class OgForTests(SimpleTestCase):
    # og:description output from description field
    def test_description(self):
        obj = _FakeObj({'@type': 'WebSite', 'name': 'Test', 'description': 'A test site'})
        result = str(og_for(obj))
        assert 'og:description' in result
        assert 'A test site' in result

    # og:url output from url field
    def test_url(self):
        obj = _FakeObj({'@type': 'WebSite', 'name': 'Test', 'url': 'https://example.com'})
        result = str(og_for(obj))
        assert 'og:url' in result
        assert 'https://example.com' in result

    # og:image with width and height from dict
    def test_image_dimensions(self):
        obj = _FakeObj(
            {
                '@type': 'WebSite',
                'name': 'Test',
                'image': {'url': 'https://example.com/img.jpg', 'width': 1200, 'height': 630},
            }
        )
        result = str(og_for(obj))
        assert 'og:image:width' in result
        assert '1200' in result
        assert 'og:image:height' in result
        assert '630' in result

    # og:image from plain string
    def test_image_from_string(self):
        obj = _FakeObj({'@type': 'WebSite', 'name': 'Test', 'image': 'https://example.com/img.jpg'})
        result = str(og_for(obj))
        assert 'og:image' in result
        assert 'https://example.com/img.jpg' in result

    # article:published_time and article:modified_time from datetime objects
    def test_article_dates(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
                'datePublished': datetime.datetime(2024, 6, 15, 14, 30),
                'dateModified': datetime.date(2024, 7, 1),
            }
        )
        result = str(og_for(obj))
        assert 'article:published_time' in result
        assert '2024-06-15T14:30:00' in result
        assert 'article:modified_time' in result
        assert '2024-07-01' in result

    # headline takes precedence over name for og:title on articles
    def test_headline_overrides_name(self):
        obj = _FakeObj({'@type': 'Article', 'name': 'Fallback', 'headline': 'Primary'})
        result = str(og_for(obj))
        assert 'Primary' in result

    # missing @type does not crash
    def test_missing_type(self):
        obj = _FakeObj({'name': 'Test', 'description': 'No type'})
        result = str(og_for(obj))
        assert 'og:title' in result
        assert 'website' in result

    # no output for objects without structured_data
    def test_no_structured_data(self):
        result = str(og_for(object()))
        assert result == ''

    # article:author extracted from dict with url key
    def test_article_author_from_dict(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
                'author': {'@type': 'Person', 'url': 'https://example.com/author'},
            }
        )
        result = str(og_for(obj))
        assert 'article:author' in result
        assert 'https://example.com/author' in result

    # article:author extracted from plain string
    def test_article_author_from_string(self):
        obj = _FakeObj(
            {
                '@type': 'BlogPosting',
                'name': 'Test',
                'author': 'Jane Doe',
            }
        )
        result = str(og_for(obj))
        assert 'article:author' in result
        assert 'Jane Doe' in result

    # article:section output from articleSection
    def test_article_section(self):
        obj = _FakeObj(
            {
                '@type': 'NewsArticle',
                'name': 'Test',
                'articleSection': 'Technology',
            }
        )
        result = str(og_for(obj))
        assert 'article:section' in result
        assert 'Technology' in result

    # keywords list produces one article:tag per keyword
    def test_article_tags_from_keywords(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
                'keywords': ['python', 'django', 'testing'],
            }
        )
        result = str(og_for(obj))
        assert result.count('article:tag') == 3
        assert 'python' in result
        assert 'django' in result
        assert 'testing' in result

    # non-article @type falls back to og:type = website
    def test_fallback_og_type(self):
        obj = _FakeObj(
            {
                '@type': 'Person',
                'name': 'John',
            }
        )
        result = str(og_for(obj))
        assert 'og:type' in result
        assert 'website' in result

    # og:image:alt extracted from image caption
    def test_image_alt_from_caption(self):
        obj = _FakeObj(
            {
                '@type': 'WebSite',
                'name': 'Test',
                'image': {'url': 'https://example.com/img.jpg', 'caption': 'A nice photo'},
            }
        )
        result = str(og_for(obj))
        assert 'og:image:alt' in result
        assert 'A nice photo' in result

    # no og:image:alt when image is a plain string
    def test_no_image_alt_for_string_image(self):
        obj = _FakeObj(
            {
                '@type': 'WebSite',
                'name': 'Test',
                'image': 'https://example.com/img.jpg',
            }
        )
        result = str(og_for(obj))
        assert 'og:image:alt' not in result


class ExtractLocationNameTests(SimpleTestCase):
    # extracts name from plain string
    def test_string_location(self):
        assert extract_location_name('Convention Center') == 'Convention Center'

    # extracts name from Place dict
    def test_dict_with_name(self):
        assert extract_location_name({'@type': 'Place', 'name': 'Convention Center'}) == 'Convention Center'

    # extracts name from nested address
    def test_nested_address_name(self):
        loc = {'@type': 'Place', 'address': {'@type': 'PostalAddress', 'name': 'Downtown Venue'}}
        assert extract_location_name(loc) == 'Downtown Venue'

    # returns None for dict without name or address.name
    def test_dict_without_name(self):
        assert extract_location_name({'@type': 'Place', 'url': 'https://example.com'}) is None

    # returns None for unsupported types
    def test_unsupported_type(self):
        assert extract_location_name(42) is None


class ExtractAuthorNameTests(SimpleTestCase):
    # extracts name from plain string
    def test_string_author(self):
        assert extract_author_name('Jane Doe') == 'Jane Doe'

    # extracts name from Person dict
    def test_dict_author(self):
        assert extract_author_name({'@type': 'Person', 'name': 'Jane Doe'}) == 'Jane Doe'

    # returns None for dict without name
    def test_dict_without_name(self):
        assert extract_author_name({'@type': 'Person', 'url': 'https://example.com'}) is None

    # returns None for unsupported types
    def test_unsupported_type(self):
        assert extract_author_name(42) is None


class MetaForTests(SimpleTestCase):
    # description meta tag output
    def test_description(self):
        obj = _FakeObj({'@type': 'Article', 'description': 'A test article'})
        result = str(meta_for(obj))
        assert 'name="description"' in result
        assert 'A test article' in result

    # no output for objects without structured_data
    def test_no_structured_data(self):
        result = str(meta_for(object()))
        assert result == ''

    # meta author extracted from string author
    def test_author_from_string(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'author': 'Jane Doe',
            }
        )
        result = str(meta_for(obj))
        assert 'name="author"' in result
        assert 'Jane Doe' in result

    # meta author extracted from Person dict
    def test_author_from_dict(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'author': {'@type': 'Person', 'name': 'John Smith'},
            }
        )
        result = str(meta_for(obj))
        assert 'name="author"' in result
        assert 'John Smith' in result

    # no author tag when author field is missing
    def test_no_author_without_field(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'description': 'A test article',
            }
        )
        result = str(meta_for(obj))
        assert 'author' not in result

    # keywords list joined with commas
    def test_keywords_from_list(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'keywords': ['python', 'django', 'web'],
            }
        )
        result = str(meta_for(obj))
        assert 'name="keywords"' in result
        assert 'python, django, web' in result

    # keywords string passed through directly
    def test_keywords_from_string(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'keywords': 'python, django',
            }
        )
        result = str(meta_for(obj))
        assert 'name="keywords"' in result
        assert 'python, django' in result

    # location extracted from Place dict
    def test_location_from_dict(self):
        obj = _FakeObj(
            {
                '@type': 'Event',
                'name': 'Conference',
                'location': {'@type': 'Place', 'name': 'Convention Center'},
            }
        )
        result = str(meta_for(obj))
        assert 'name="location"' in result
        assert 'Convention Center' in result

    # location extracted from string
    def test_location_from_string(self):
        obj = _FakeObj(
            {
                '@type': 'Event',
                'name': 'Meetup',
                'location': 'City Hall',
            }
        )
        result = str(meta_for(obj))
        assert 'name="location"' in result
        assert 'City Hall' in result


class TwitterForTests(SimpleTestCase):
    # articles get summary_large_image card type
    def test_article_card_type(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
            }
        )
        result = str(twitter_for(obj))
        assert 'twitter:card' in result
        assert 'summary_large_image' in result

    # non-article types get summary card type
    def test_default_card_type(self):
        obj = _FakeObj(
            {
                '@type': 'WebSite',
                'name': 'Test',
            }
        )
        result = str(twitter_for(obj))
        assert 'twitter:card' in result
        assert 'summary' in result
        assert 'summary_large_image' not in result

    # twitter:image from dict image
    def test_image_from_dict(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
                'image': {'url': 'https://example.com/img.jpg', 'caption': 'A photo'},
            }
        )
        result = str(twitter_for(obj))
        assert 'twitter:image' in result
        assert 'https://example.com/img.jpg' in result

    # twitter:image from plain string
    def test_image_from_string(self):
        obj = _FakeObj(
            {
                '@type': 'WebSite',
                'name': 'Test',
                'image': 'https://example.com/photo.jpg',
            }
        )
        result = str(twitter_for(obj))
        assert 'twitter:image' in result
        assert 'https://example.com/photo.jpg' in result

    # image alt text extracted from image caption
    def test_image_alt_from_caption(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
                'image': {'url': 'https://example.com/img.jpg', 'caption': 'A photo'},
            }
        )
        result = str(twitter_for(obj))
        assert 'twitter:image:alt' in result
        assert 'A photo' in result

    # twitter:creator from string author
    def test_creator_from_author(self):
        obj = _FakeObj(
            {
                '@type': 'Article',
                'name': 'Test',
                'author': 'Jane Doe',
            }
        )
        result = str(twitter_for(obj))
        assert 'twitter:creator' in result
        assert 'Jane Doe' in result

    # events get summary_large_image card type
    def test_event_card_type(self):
        obj = _FakeObj(
            {
                '@type': 'Event',
                'name': 'Conference',
            }
        )
        result = str(twitter_for(obj))
        assert 'summary_large_image' in result

    # no output for objects without structured_data
    def test_no_structured_data(self):
        result = str(twitter_for(object()))
        assert result == ''


class ResolveStructuredDataTests(SimpleTestCase):
    # returns dict as-is
    def test_dict_passthrough(self):
        data = {'@type': 'WebSite', 'name': 'Test'}
        assert resolve_structured_data(data) is data

    # returns structured_data attribute from object
    def test_object_attribute(self):
        obj = _FakeObj({'@type': 'WebSite', 'name': 'Test'})
        assert resolve_structured_data(obj) == {'@type': 'WebSite', 'name': 'Test'}

    # returns None for unsupported input
    def test_unsupported_input(self):
        assert resolve_structured_data(42) is None
        assert resolve_structured_data('hello') is None
        assert resolve_structured_data(object()) is None


class DictPassthroughTests(SimpleTestCase):
    # json_ld_for renders a plain dict
    def test_json_ld_for_dict(self):
        result = str(json_ld_for({'@type': 'WebSite', 'name': 'Test'}))
        assert '<script type="application/ld+json">' in result
        assert 'https://schema.org' in result
        assert 'Test' in result

    # og_for renders a plain dict
    def test_og_for_dict(self):
        result = str(og_for({'@type': 'WebSite', 'name': 'Test', 'description': 'A site'}))
        assert 'og:title' in result
        assert 'og:description' in result

    # meta_for renders a plain dict
    def test_meta_for_dict(self):
        result = str(meta_for({'@type': 'Article', 'description': 'A test'}))
        assert 'name="description"' in result
        assert 'A test' in result

    # twitter_for renders a plain dict
    def test_twitter_for_dict(self):
        result = str(twitter_for({'@type': 'Article', 'name': 'Test'}))
        assert 'twitter:card' in result
        assert 'summary_large_image' in result

    # all tags return empty string for non-dict, non-object input
    def test_all_tags_empty_for_invalid(self):
        assert str(json_ld_for(42)) == ''
        assert str(og_for(42)) == ''
        assert str(meta_for(42)) == ''
        assert str(twitter_for(42)) == ''

    # json_ld_for does not mutate the original dict
    def test_json_ld_for_no_mutation(self):
        data = {'@type': 'WebSite', 'name': 'Test'}
        json_ld_for(data)
        assert '@context' not in data


class StructuredDataMixinTests(SimpleTestCase):
    # mixin injects structured_data into template context
    def test_injects_context(self):
        class TestView(StructuredDataMixin, TemplateView):
            template_name = 'test.html'

            def get_structured_data(self):
                return {'@type': 'WebSite', 'name': 'Test'}

        request = RequestFactory().get('/')
        view = TestView()
        view.setup(request)
        context = view.get_context_data()
        assert context['structured_data'] == {'@type': 'WebSite', 'name': 'Test'}

    # mixin does not inject when get_structured_data returns None
    def test_no_injection_on_none(self):
        class TestView(StructuredDataMixin, TemplateView):
            template_name = 'test.html'

        request = RequestFactory().get('/')
        view = TestView()
        view.setup(request)
        context = view.get_context_data()
        assert 'structured_data' not in context

    # mixin preserves other context from super
    def test_cooperative_inheritance(self):
        class TestView(StructuredDataMixin, TemplateView):
            template_name = 'test.html'

            def get_structured_data(self):
                return {'@type': 'WebSite'}

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['extra'] = 'value'
                return context

        request = RequestFactory().get('/')
        view = TestView()
        view.setup(request)
        context = view.get_context_data()
        assert context['structured_data'] == {'@type': 'WebSite'}
        assert context['extra'] == 'value'


class JsonLdSitewideTests(SimpleTestCase):
    # renders all items from setting
    @override_settings(
        STRUCTURED_DATA_SITEWIDE=[
            {'@type': 'Organization', 'name': 'Acme'},
            {'@type': 'WebSite', 'name': 'Acme Site'},
        ]
    )
    def test_renders_all_items(self):
        result = str(json_ld_sitewide())
        assert result.count('<script type="application/ld+json">') == 2
        assert 'Acme' in result
        assert 'Acme Site' in result

    # adds @context when missing
    @override_settings(STRUCTURED_DATA_SITEWIDE=[{'@type': 'Organization', 'name': 'Test'}])
    def test_adds_context(self):
        result = str(json_ld_sitewide())
        assert 'https://schema.org' in result

    # preserves existing @context
    @override_settings(
        STRUCTURED_DATA_SITEWIDE=[
            {'@context': 'https://custom.org', '@type': 'Organization', 'name': 'Test'},
        ]
    )
    def test_preserves_existing_context(self):
        result = str(json_ld_sitewide())
        assert 'https://custom.org' in result
        assert 'schema.org' not in result

    # returns empty string when setting is absent
    def test_empty_when_absent(self):
        result = str(json_ld_sitewide())
        assert result == ''

    # XSS-sensitive characters are escaped
    @override_settings(STRUCTURED_DATA_SITEWIDE=[{'@type': 'Organization', 'name': '<script>alert("xss")</script>'}])
    def test_xss_escaping(self):
        result = str(json_ld_sitewide())
        assert '<script>alert' not in result
        assert '\\u003C' in result

    # does not mutate the original setting dicts
    @override_settings(STRUCTURED_DATA_SITEWIDE=[{'@type': 'Organization', 'name': 'Test'}])
    def test_no_mutation(self):
        from django.conf import settings

        json_ld_sitewide()
        assert '@context' not in settings.STRUCTURED_DATA_SITEWIDE[0]


class OgSitewideTests(SimpleTestCase):
    # renders properties from setting
    @override_settings(STRUCTURED_DATA_SITEWIDE_OG={'og:site_name': 'My Site', 'og:locale': 'en_US'})
    def test_renders_properties(self):
        result = str(og_sitewide())
        assert 'og:site_name' in result
        assert 'My Site' in result
        assert 'og:locale' in result
        assert 'en_US' in result

    # returns empty string when setting is absent
    def test_empty_when_absent(self):
        result = str(og_sitewide())
        assert result == ''

    # HTML-escapes content values
    @override_settings(STRUCTURED_DATA_SITEWIDE_OG={'og:site_name': 'A & B <script>'})
    def test_html_escaping(self):
        result = str(og_sitewide())
        assert '&amp;' in result
        assert '<script>' not in result
