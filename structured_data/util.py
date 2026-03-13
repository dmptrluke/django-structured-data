import datetime
import json
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html_join

ARTICLE_TYPES = ('Article', 'BlogPosting', 'NewsArticle')

EVENT_TYPES = (
    'Event',
    'BusinessEvent',
    'ChildrensEvent',
    'ComedyEvent',
    'DanceEvent',
    'EducationEvent',
    'ExhibitionEvent',
    'Festival',
    'FoodEvent',
    'Hackathon',
    'LiteraryEvent',
    'MusicEvent',
    'ScreeningEvent',
    'SocialEvent',
    'SportsEvent',
    'TheaterEvent',
    'VisualArtsEvent',
)

LARGE_IMAGE_TYPES = ARTICLE_TYPES + EVENT_TYPES + ('Recipe',)

_json_script_escapes = {
    ord('>'): '\\u003E',
    ord('<'): '\\u003C',
    ord('&'): '\\u0026',
}


def json_encode(data: dict[str, Any]) -> str:
    return json.dumps(data, cls=DjangoJSONEncoder).translate(_json_script_escapes)


def format_time(value: Any) -> Any:
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    return value


def build_og_tags(properties: list[tuple[str, Any]]) -> str:
    formatted = ((k, format_time(v)) for k, v in properties)
    return format_html_join('\n', '<meta property="{}" content="{}" />', formatted)


def build_meta_tags(properties: dict[str, Any]) -> str:
    formatted = ((k, format_time(v)) for k, v in properties.items())
    return format_html_join('\n', '<meta name="{}" content="{}" />', formatted)


def resolve_structured_data(obj: Any) -> dict | None:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, 'structured_data'):
        return obj.structured_data
    return None


def extract_author_name(author: Any) -> str | None:
    if isinstance(author, str):
        return author
    if isinstance(author, dict) and 'name' in author:
        return author['name']
    return None


def extract_location_name(location: Any) -> str | None:
    if isinstance(location, str):
        return location
    if isinstance(location, dict):
        if 'name' in location:
            return location['name']
        if isinstance(location.get('address'), dict) and 'name' in location['address']:
            return location['address']['name']
    return None
