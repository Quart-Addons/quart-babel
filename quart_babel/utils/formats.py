"""
quart_babel.utils.formats

This module provides utils for for formatting
text, numbers, and dates.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from numbers import Number
from typing import Any, Callable, Optional, Union, TYPE_CHECKING
from babel import dates, numbers

from .context import get_state
from .locale import get_locale
from .timezone import get_timezone, to_user_timezone

if TYPE_CHECKING:
    from quart_babel.core import _BabelState

def _get_format(key: str, format: Optional[str]=None) -> str:
    """A small helper for the datetime formatting functions.  Looks up
    format defaults for different kinds.
    """
    state: _BabelState = get_state()
    if format is None:
        format = state.babel.date_formats[key]
    if format in ('short', 'medium', 'full', 'long'):
        return_val = state.babel.date_formats[f'{key}.{format}']
        if return_val is not None:
            format = return_val
    return format

async def format_datetime(
    datetime: Optional[datetime]=None,
    format: Optional[str]=None,
    rebase: bool=True
    ) -> str:
    """Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function formats both date and
    time.
    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which case the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.
    This function is also available in the template context as filter
    named `datetimeformat`.
    """
    format = _get_format('datetime', format)
    return await _date_format(dates.format_datetime, datetime, format, rebase)


async def format_date(
    date: Optional[Union[datetime, date]]=None,
    format: Optional[str]=None,
    rebase: bool=True
    ) -> str:
    """Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` or :class:`~datetime.date` object is passed,
    the current time is assumed.  By default rebasing happens which causes
    the object to be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function only formats the date part
    of a :class:`~datetime.datetime` object.
    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.
    This function is also available in the template context as filter
    named `dateformat`.
    """
    if rebase and isinstance(date, datetime):
        date = await to_user_timezone(date)
    format = _get_format('date', format)
    return await _date_format(dates.format_date, date, format, rebase)


async def format_time(
    time: datetime=None,
    format: Optional[str]=None,
    rebase: bool=True
    ) -> str:
    """Return a time formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function formats both date and
    time.
    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.
    This function is also available in the template context as filter
    named `timeformat`.
    """
    format = _get_format('time', format)
    return await _date_format(dates.format_time, time, format, rebase)


async def format_timedelta(
    datetime_or_timedelta: Union[datetime, timedelta],
    granularity: str='second',
    add_direction: bool=False,
    threshold: float=0.85
    ) -> str:
    """Format the elapsed time from the given date to now or the given
    timedelta.
    This function is also available in the template context as filter
    named `timedeltaformat`.
    """
    if isinstance(datetime_or_timedelta, datetime):
        datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta

    locale = await get_locale()

    return dates.format_timedelta(
        datetime_or_timedelta,
        granularity,
        threshold=threshold,
        add_direction=add_direction,
        locale=locale
    )


async def _date_format(
    formatter: Callable,
    obj: Any,
    format: str,
    rebase: bool,
    **extra
    ) -> str:
    """Internal helper that formats the date."""
    locale = await get_locale()
    extra = {}
    if formatter is not dates.format_date and rebase:
        extra['tzinfo'] = await get_timezone()
    return formatter(obj, format, locale=locale, **extra)


async def format_number(number: Number) -> str:
    """Return the given number formatted for the locale in request
    :param number: the number to format
    :return: the formatted number
    :rtype: unicode
    """
    locale = await get_locale()
    return numbers.format_decimal(number, locale=locale)


async def format_decimal(number: Number, format: Optional[str]=None) -> str:
    """Return the given decimal number formatted for the locale in request
    :param number: the number to format
    :param format: the format to use
    :return: the formatted number
    :rtype: unicode
    """
    locale = await get_locale()
    return numbers.format_decimal(number, format=format, locale=locale)


async def format_currency(
    number: Number,
    currency: str,
    format: Optional[str]=None,
    currency_digits: bool=True,
    format_type: str='standard'
    ) -> str:
    """Return the given number formatted for the locale in request

    :param number: the number to format
    :param currency: the currency code
    :param format: the format to use
    :param currency_digits: use the currency’s number of decimal digits [default: True]
    :param format_type: the currency format type to use [default: standard]

    :return: the formatted number
    :rtype: unicode
    """
    locale = await get_locale()
    return numbers.format_currency(
        number,
        currency,
        format=format,
        locale=locale,
        currency_digits=currency_digits,
        format_type=format_type
    )


async def format_percent(
    number: Number,
    format: Optional[str]=None
    ) -> str:
    """Return formatted percent value for the locale in request
    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = await get_locale()
    return numbers.format_percent(number, format=format, locale=locale)


async def format_scientific(
    number: Number,
    format: str=None
    ) -> str:
    """Return value formatted in scientific notation for the locale in request
    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = await get_locale()
    return numbers.format_scientific(number, format=format, locale=locale)
