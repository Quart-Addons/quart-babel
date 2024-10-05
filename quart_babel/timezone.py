"""
quart_babel.timezone
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from pytz import BaseTzInfo, timezone, UTC
from .utils import get_babel, _get_current_context


def get_timezone() -> Optional[BaseTzInfo]:
    """
    Returns the timezone that should be used for this request as
    a `pytz.timezone` object.  This returns `None` if used outside
    a request.
    """
    ctx = _get_current_context()
    tzinfo = getattr(ctx, "babel_tzinfo", None)

    if tzinfo is None:
        babel = get_babel()

        if babel.timezone_selector is None:
            tzinfo = babel.instance.default_timezone
        else:
            rv = babel.timezone_selector()

            if rv is None:
                tzinfo = babel.instance.default_timezone
            else:
                tzinfo = timezone(rv) if isinstance(rv, str) else rv

        ctx.babel_tzinfo = tzinfo

    return tzinfo


def to_user_timezone(dt: datetime) -> datetime:
    """
    Convert a datetime object to the user's timezone.  This automatically
    happens on all date formatting unless rebasing is disabled.  If you need
    to convert a :class:`datetime.datetime` object at any time to the user's
    timezone (as returned by :func:`get_timezone`) this function can be used.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    tzinfo = get_timezone()
    return tzinfo.normalize(dt.astimezone(tzinfo))


def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime object to the user's timezone.  This automatically
    happens on all date formatting unless rebasing is disabled.  If you need
    to convert a :class:`datetime.datetime` object at any time to the user's
    timezone (as returned by :func:`get_timezone`) this function can be used.
    """
    if dt.tzinfo is None:
        dt = get_timezone().localize(dt)
    return dt.astimezone(UTC).replace(tzinfo=None)
