import datetime

from django.test import SimpleTestCase

from .util import build_meta_tags, build_og_tags, format_time


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
        props = {'article:published_time': datetime.datetime(2024, 6, 15, 14, 30)}
        result = str(build_og_tags(props))
        assert '2024-06-15T14:30:00' in result

    # date values in OG tags are formatted as YYYY-MM-DD
    def test_date_in_og_tags(self):
        props = {'article:published_time': datetime.date(2024, 6, 15)}
        result = str(build_og_tags(props))
        assert '2024-06-15' in result


class BuildMetaTagsTests(SimpleTestCase):
    # datetime values in meta tags are formatted as ISO 8601
    def test_datetime_in_meta_tags(self):
        props = {'date': datetime.datetime(2024, 6, 15, 14, 30)}
        result = str(build_meta_tags(props))
        assert '2024-06-15T14:30:00' in result
