"""
quart_babel.timezone
"""
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from .const import UTC
from .context import TimezoneStorageContext
from .typing import BaseTzInfo

_current_timezone = TimezoneStorageContext()


def setup_timezone_context(default_timezone: BaseTzInfo | str) -> None:
    """
     Setups context with the default locale value using
    :func:`LocaleStorageContext.setup_context` method.

    Arguments:
        default_timezone: The default timezone to use.
    """
    _current_timezone.setup_context(default_timezone)


def get_timezone() -> BaseTzInfo:
    """
    Gets the current active timezone from context.
    """
    return _current_timezone.get()


def set_timezone(timezone: str | BaseTzInfo) -> None:
    """
    Sets the active timezone to context.

    Part of the internal API.

    Arguments:
        timezone: The timezone to set.
    """
    _current_timezone.set(timezone)


@contextmanager
def switch_timezone(timezone: str | BaseTzInfo) -> Generator[None, None, None]:
    """
    Temporary switch current timezone for a code block. The previous timezone
    will be restored after exiting the manager.

    Arguments:
        timezone: The timezone to switch to.
    """
    old_timezone = get_timezone()
    set_timezone(timezone)
    yield
    set_timezone(old_timezone)


def refresh_timezone(timezone: BaseTzInfo | str | None = None) -> None:
    """
    Refreshes the cached timezone information. This can be used
    to switch a timezone between a request and if you want the
    changes to take place immediately, not just with the next
    request.

    Arguments:
        timezone: The timezone to set. If none is used it will use the default
            timezone.
    """
    _current_timezone.refresh(timezone)


def to_user_timezone(dtime: datetime) -> datetime:
    """
    Convert a datetime object to the user's timezone.  This automatically
    happens on all date formatting unless rebasing is disabled.  If you need
    to convert a :class:`datetime.datetime` object at any time to the user's
    timezone (as returned by :func:`get_timezone` this function can be used).

    Arguments:
        dtime: The datetime object to use the user's timezone.
    """
    if dtime.tzinfo is None:
        dtime = dtime.replace(tzinfo=UTC)

    tzinfo = get_timezone()

    return dtime.astimezone(tzinfo)


def to_utc(dtime: datetime) -> datetime:
    """
    Convert a datetime object to UTC and drop tzinfo.  This is the
    opposite operation to :func:`to_user_timezone`.

    Arguments:
        dttime (`datetime`): The datetime object to convert.
    """
    if dtime.tzinfo is None:
        dtime = get_timezone().localize(dtime)
    return dtime.astimezone(UTC).replace(tzinfo=None)
