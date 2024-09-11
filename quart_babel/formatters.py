"""
quart_babel.formatters

Provides format helpers for Quart-Babel.
"""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import typing as t

from babel import dates, numbers

from .locale import get_locale
from .timezone import get_timezone, to_user_timezone
from .typing import DateTimeFormats, Granularity
from .utils import get_state


def _date_format(
    formatter: t.Callable,
    obj: t.Any,
    format: str,
    rebase: bool,
    **extra: t.Any
) -> str:
    """
    This helper function helps format a date.

    It will also get the locale from context. If timezone
    info is to be used. The function will also get the
    current timezone from context.

    Part of the internal API.

    Arguments:
        formatter: The formatter to use.
        object: The object to format.
        format: The format to use.
        rebase: Determines to use user timezone or not.
        extra:" Kwargs to pass to the formatter.
    """
    locale = get_locale()
    extra = {}

    if formatter is not dates.format_date and rebase:
        extra['tzinfo'] = get_timezone()

    return formatter(obj, format, locale=locale, **extra)


def _get_format(key: str, format: str | None = None) -> str:
    """
    A small helper for the datetime formatting functions.  Looks up
    format defaults for different kinds.

    Part of the internal API.

    Arguments:
        key: The dictionary key to use.
        format: The format to use (Defaults to ``None``).
    """
    state = get_state()

    if format is None:
        format = state.babel.date_formats[key]

    if format in ('short', 'medium', 'full', 'long'):
        return_val = state.babel.date_formats[f'{key}.{format}']

    if return_val is not None:
        format = return_val

    return format


def format_datetime(
    dt: datetime | None = None,
    format: DateTimeFormats | None = None,
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
    format = _get_format('datetime', format)
    return _date_format(dates.format_datetime, dt, format, rebase)


def format_date(
    dt: datetime | date | None = None,
    format: DateTimeFormats | None = None,
    rebase: bool = True
) -> str:
    """
    Return a date formatted according to the given pattern.  If no
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

    Arguments:
        dt: The date to format. If no date is provided, it will use the
            current date.
        format: The format to use.
        rebase: Determines to use user timezone or not.
    """
    if rebase and isinstance(dt, datetime):
        dt = to_user_timezone(dt)

    format = _get_format('date', format)

    return _date_format(dates.format_date, dt, format, rebase)


def format_time(
    time: time | datetime | float | None = None,
    format: DateTimeFormats | None = None,
    rebase: bool = True
) -> str:
    """
    Return a time formatted according to the given pattern.  If no
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

    Arguments:
        time: The time to format. If no time is provided, it will use the
            current time.
        format: The format to use.
        rebase: Determines to use user timezone or not.
    """
    format = _get_format('time', format)
    return _date_format(dates.format_time, time, format, rebase)


def format_timedelta(
    delta: datetime | timedelta | int,
    granularity: Granularity = "second",
    threshold: float = 0.85,
    add_direction: bool = False
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
    if isinstance(delta, datetime):
        delta = datetime.utcnow() - delta

    return dates.format_timedelta(
        delta,
        granularity,
        threshold=threshold,
        add_direction=add_direction,
        locale=get_locale()
    )


def format_interval(
    start: datetime | date | time,
    end: datetime | date | time,
    skeleton: str | None = None,
    fuzzy: bool = True,
    rebase: bool = True
) -> str:
    """
    Format an interval between two instants according to the locale's rules.

    Arguments:
        start: First instance.
        end: Second instance.
        skeleton: The "skeleton format" to use for formatting.
        fuzzy: If the skeleton is not found, allow choosing a skeleton that is
            close enough to it.
        rebase: Determines to use user timezone or not. Defaults to ``True``.
    """
    if type(start) is not type(end):
        raise TypeError('"start" and "end" parameters must be the same type.')

    extra_kwargs = {}

    if rebase:
        extra_kwargs["tzinfo"] = get_timezone()

    return dates.format_interval(
        start,
        end,
        skeleton=skeleton,
        fuzzy=fuzzy,
        locale=get_locale(),
        **extra_kwargs
    )


def format_number(number: float | Decimal | str) -> str:
    """
    Return the given number formatted for the locale.

    This function will return :func:`quart_babel.format_decimal` function,
    since the :func:`babel.numbers.format_number` function is depreciated.

    Arguments:
        number: The number to format.
    """
    return format_decimal(number)


def format_decimal(
    number: float | Decimal | str,
    format: str | None = None,
    decimal_quantization: bool = True,
    group_separator: bool = True
) -> str:
    """
    Returns the given decimal number formatted for a specific locale.

    Arguments:
        number: The number to format.
        format: The format to use.
        decimal_quantization: Truncate and round high-precision numbers to
            the format pattern.
        group_separator: Boolean to switch group separator on/off in a
            locale's number format.
    """
    return numbers.format_decimal(
        number,
        format=format,
        locale=get_locale(),
        decimal_quantization=decimal_quantization,
        group_separator=group_separator
        )


def format_currency(
    number: float | Decimal | str,
    currency: str,
    format: str | None = None,
    currency_digits: bool = True,
    format_type: t.Literal["name", "standard", "accounting"] = "standard",
    decimal_quantization: bool = True,
    group_separator: bool = True
) -> str:
    """
    Returns formatted currency value.

    Arguments:
        number: the number to format.
        currency: the currency code.
        format: the format string to use.
        currency_digits: use the currency's natural number of decimal digits.
        format_type: the currency format type to use.
        decimal_quantization: Truncate and round high-precision numbers.
            The format pattern.
        group_separator: Boolean to switch group separator on/off in a locale's
            number format.
    """
    value = numbers.format_currency(
        number,
        currency,
        format=format,
        locale=get_locale(),
        currency_digits=currency_digits,
        format_type=format_type,
        decimal_quantization=decimal_quantization,
        group_separator=group_separator
    )

    return value


def format_percent(
    number: float | Decimal | str,
    format: str | None = None,
    decimal_quantization: bool = True,
    group_separator: bool = True
) -> str:
    """
    Returns a formatted percent value for a specific locale.

    Arguments:
        number: The percent number to format
        format: The format to use.
        decimal_quantization: Truncate and round high-precision numbers to
            the format pattern.
        group_separator: Boolean to switch group separator on/off in a locale's
            number format.
    """
    return numbers.format_percent(
        number,
        format=format,
        locale=get_locale(),
        decimal_quantization=decimal_quantization,
        group_separator=group_separator
        )


def format_scientific(
    number: float | Decimal | str,
    format: str | None = None,
    decimal_quantization: bool = True
) -> str:
    """
    Returns a value formatted in scientific notation for a specific locale.

    Arguments:
        number: The number to format.
        format: The format to use.
        decimal_quantization: Truncate and round high-precision numbers to the
            format pattern.
    """
    return numbers.format_scientific(
        number,
        format=format,
        locale=get_locale(),
        decimal_quantization=decimal_quantization
        )
