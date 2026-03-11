import datetime

from django.test import SimpleTestCase

from .templatetags.jsonld import json_ld_for
from .templatetags.meta import meta_for
from .templatetags.opengraph import og_for
from .templatetags.twitter import twitter_for
from .util import build_meta_tags, build_og_tags, extract_author_name, extract_location_name, format_time, json_encode


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
