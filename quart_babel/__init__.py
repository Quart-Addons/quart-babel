"""
Quart Babel

An extension to `Quart` that adds i18n and i10n support to any :mod:`Quart`
application with the help of `babel`, `pytz`, and `speaklater`. It has builtin
support for date formatting with timezone support as well as a very simple and
friendly interface :mod:`gettext` translations.
"""
from .core import Babel

from .domain import (
    Domain,
    gettext,
    ngettext,
    pgettext,
    npgettext,
    lazy_gettext,
    lazy_ngettext,
    lazy_pgettext
)

from .formatters import (
    format_datetime,
    format_date,
    format_time,
    format_timedelta,
    format_interval,
    format_number,
    format_decimal,
    format_currency,
    format_percent,
    format_scientific
)

from .locale import (
    get_locale,
    switch_locale,
    refresh_locale,
    select_locale_by_request
    )

from .timezone import (
    get_timezone,
    switch_timezone,
    refresh_timezone,
    to_user_timezone,
    to_utc,
    select_timezone_by_request
    )

__all__ = (
    'Babel',
    'Domain',
    'gettext',
    'ngettext',
    'pgettext',
    'npgettext',
    'lazy_gettext',
    'lazy_ngettext',
    'lazy_pgettext',
    'format_datetime',
    'format_date',
    'format_time',
    'format_timedelta',
    'format_interval',
    'format_number',
    'format_decimal',
    'format_currency',
    'format_percent',
    'format_scientific',
    'get_locale',
    'switch_locale',
    'refresh_locale',
    'select_locale_by_request',
    'get_timezone',
    'switch_timezone',
    'refresh_timezone',
    'to_user_timezone',
    'to_utc',
    'select_timezone_by_request'
)
