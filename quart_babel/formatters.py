"""
get_babel.formatters
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Callable, Literal, Optional, Union

from babel import dates, numbers
from babel.numbers import NumberPattern

from .locale import get_locale
from .timezone import get_timezone, to_user_timezone
from .utils import get_babel


# pylint: disable=W0621
# pylint: disable=W0622

DateTimeFormats = Literal["short", "medium", "long", "full"]

TimeDeltaFormats = Literal["narrow", "short", "long"]

Granularity = Literal[
    "year", "month", "week", "day", "hour", "minute", "second"
]


def _get_format(key: str, format: Optional[str] = None) -> Optional[str]:
    """
    A small helper for the datetime formatting functions.  Looks up
    format defaults for different kinds.
    """
    babel = get_babel()
    if format is None:
        format = babel.instance.date_formats[key]
    if format in ("short", "medium", "full", "long"):
        rv = babel.instance.date_formats[f'{key}.{format}']
        if rv is not None:
            format = rv
    return format


def _date_format(
        formatter: Callable,
        obj: Any,
        format: str,
        rebase: bool,
        **extra: Any
) -> str:
    """Internal helper that formats the date."""
    locale = get_locale()
    extra = {}
    if formatter is not dates.format_date and rebase:
        extra["tzinfo"] = get_timezone()
    return formatter(obj, format, locale=locale, **extra)


def format_datetime(
        dt: Optional[datetime] = None,
        format: Optional[DateTimeFormats] = None,
        rebase: bool = True
) -> str:
    """
    Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).

    This function formats both date and time. The format parameter can either
    be ``'short'``, ``'medium'``, ``'long'`` or ``'full'`` (in which case the
    language's default for that setting is used, or the default from the
    :attr:`Babel.date_formats` mapping is used) or a format string as
    documented by Babel. This function is also available in the template
    context as filter named `datetimeformat`.

    Arguments:
        dt: The date to format. If no date is provided, it will use the
            current date.
        format: The format to use (Defaults to ``None``).
        rebase (``bool``): Determines to use user timezone or not.
    """
    format = _get_format("datetime", format)
    return _date_format(dates.format_datetime, dt, format, rebase)


def format_date(
        dt: Optional[Union[date, datetime]] = None,
        format: Optional[DateTimeFormats] = None,
        rebase: bool = True
) -> str:
    """
    Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` or :class:`~datetime.date` object is passed,
    the current time is assumed.  By default, rebasing happens, which causes
    the object to be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function only formats the date part
    of a :class:`~datetime.datetime` object.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which case the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `dateformat`.
    """
    if rebase and isinstance(dt, datetime):
        dt = to_user_timezone(dt)

    format = _get_format('date', format)

    return _date_format(dates.format_date, dt, format, rebase)


def format_time(
        time: Optional[Union[time, datetime, float]] = None,
        format: Optional[DateTimeFormats] = None,
        rebase: bool = True
) -> str:
    """
    Return a time formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default, rebasing happens, which causes the object to
    be converted to the user's timezone (as returned by
    :func:`to_user_timezone`).  This function formats both date and time.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which case the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `timeformat`.
    """
    format = _get_format('time', format)
    return _date_format(dates.format_time, time, format, rebase)


def format_timedelta(
        datetime_or_timedelta: Union[datetime, timedelta, int],
        granularity: Granularity = "second",
        add_direction: bool = False,
        threshold: float = 0.85
) -> str:
    """
    Format the elapsed time from the given date to now or the given
    timedelta.

    This function is also available in the template context as filter
    named `timedeltaformat`.

    Arguments:
        delta: The time difference to format, or the delta in seconds as an
            `int` value.
        granularity: Determines the smallest unit that should be displayed,
            the value can be one of "year", "month", "week", "day", "hour",
            "minute" or "second".
        threshold: Factor that determines at which point the presentation
            switches to the nexthigher unit.
        add_direction: If this flag is set to `True` the return value will
            include directional information. For instance a positive timedelta
            will include the information about it being in the future, a
            negative will be information about the value being in the past.
    """
    if isinstance(datetime_or_timedelta, datetime):
        datetime_or_timedelta = datetime.now() - datetime_or_timedelta
    return dates.format_timedelta(
        datetime_or_timedelta,
        granularity,
        threshold=threshold,
        add_direction=add_direction,
        locale=get_locale()
    )


def format_number(number: Union[float, Decimal, str]) -> str:
    """
    Return the given number formatted for the locale in request

    :param number: the number to format
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_decimal(number, locale=locale)


def format_decimal(
        number: Union[float, Decimal, str],
        format: Optional[str] = None
) -> str:
    """
    Return the given decimal number formatted for the locale in the request.

    :param number: the number to format
    :param format: the format to use
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_decimal(number, format=format, locale=locale)


def format_currency(
        number: Union[float, Decimal, str],
        currency: str,
        format: Optional[Union[str, NumberPattern]] = None,
        currency_digits: bool = True,
        format_type: Literal["name", "standard", "accounting"] = 'standard'

) -> str:
    """
    Return the given number formatted for the locale in the request.

    :param number: the number to format
    :param currency: the currency code
    :param format: the format to use
    :param currency_digits: use the currency's number of decimal digits
                            [default: True]
    :param format_type: the currency format type to use
                        [default: standard]
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_currency(
        number,
        currency,
        format=format,
        locale=locale,
        currency_digits=currency_digits,
        format_type=format_type
    )


def format_percent(
        number: Union[float, Decimal, str],
        format: Optional[Union[str, NumberPattern]] = None
) -> str:
    """
    Return formatted percent value for the locale in the request.

    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_percent(number, format=format, locale=locale)


def format_scientific(
        number: Union[float, Decimal, str],
        format: Optional[Union[str, NumberPattern]] = None
) -> str:
    """
    Return value formatted in scientific notation for the locale in request

    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_scientific(number, format=format, locale=locale)
