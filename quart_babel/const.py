"""
quart_babel.const
"""
from babel.util import UTC as _UTC
from werkzeug.datastructures import ImmutableDict

DEFAULT_LOCALE = "en_US"

DEFAULT_TIMEZONE = "UTC"

DEFAULT_SHORT = "short"

DEFAULT_MEDIUM = "medium"

DEFAULT_LONG = "long"

DEFAULT_FULL = "full"

DEFAULT_NARROW = "narrow"

DEFAULT_DATE_FORMATS = ImmutableDict({
    'time': DEFAULT_MEDIUM,
    'date': DEFAULT_MEDIUM,
    'datetime': DEFAULT_MEDIUM,
    'time.short': None,
    'time.medium': None,
    'time.full': None,
    'time.long': None,
    'date.short': None,
    'date.medium': None,
    'date.full': None,
    'date.long': None,
    'datetime.short': None,
    'datetime.medium': None,
    'datetime.full': None,
    'datetime.long': None,
})

UTC = _UTC
