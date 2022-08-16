"""
quart_babel.utils.timezone

This module provides utils for determining
the user timezone.
"""
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Union
from ipaddress import ip_address
import ipapi
from pytz import timezone, UTC
from quart import current_app, request
from quart.utils import is_coroutine_function, run_sync

from .context import get_state, _get_current_context

if TYPE_CHECKING:
    from quart_babel.core import _BabelState

async def get_timezone():
    """Returns the timezone that should be used for this request as
    `pytz.timezone` object.  This returns `None` if used outside of
    a request.
    """
    ctx = _get_current_context()

    if ctx is None:
        # outside of an request context
        return None

    tzinfo = getattr(ctx, 'babel_tzinfo', None)
    state: _BabelState = get_state()

    if tzinfo is None:
        if state.babel.timezone_selector_func is not None:
            if is_coroutine_function(state.babel.timezone_selector_func):
                result = await state.babel.timezone_selector_func()
            else:
                result = await run_sync(state.babel.timezone_selector_func)()

            if result is None:
                tzinfo = state.babel.default_timezone
            else:
                if isinstance(result, str):
                    tzinfo = timezone(result)
                else:
                    tzinfo = result
        else:
            tzinfo = state.babel.default_timezone
        ctx.babel_tzinfo = tzinfo
    return tzinfo

async def select_timezone_by_request() -> Optional[str]:
    """
    Select the timezone by a given request.
    """
    tzone = None

    ipapi_key = current_app.config.get('BABEL_IPAPI_KEY', None)
    ip_addr = _get_ip_address()

    if ip_address is not None:
        ip_info = ipapi.location(ip_addr, ipapi_key)
        tzone = ip_info.get('timezone', None)

    return tzone

async def to_user_timezone(datetime: datetime) -> Union[datetime, Any]:
    """Convert a datetime object to the user's timezone.  This automatically
    happens on all date formatting unless rebasing is disabled.  If you need
    to convert a :class:`datetime.datetime` object at any time to the user's
    timezone (as returned by :func:`get_timezone` this function can be used).
    """
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=UTC)
    tzinfo = await get_timezone()
    return tzinfo.normalize(datetime.astimezone(tzinfo))

async def to_utc(datetime: datetime) -> datetime:
    """Convert a datetime object to UTC and drop tzinfo.  This is the
    opposite operation to :func:`to_user_timezone`.
    """
    if datetime.tzinfo is None:
        datetime = (await get_timezone()).localize(datetime)
    return datetime.astimezone(UTC).replace(tzinfo=None)

def _get_ip_address():
    """ Makes the best attempt to get the client's real IP
    or return the loopback.
    """
    possible_headers = ['X-Forwarded-For', 'Forwarded', 'X-Real-IP']

    ip_addr = ''
    for header in possible_headers:
        possible_ip = request.headers.get(header)
        if possible_ip:
            if 'for' in possible_ip and '=' in possible_ip:
                # Using new-ish `FORWADED` header
                # https://en.wikipedia.org/wiki/X-Forwarded-For#Alternatives_and_variations
                possible_ip = possible_ip.split('=')[1]
            if ',' in possible_ip:
                # Assume first IP address in list is the originating IP address
                # https://en.wikipedia.org/wiki/X-Forwarded-For#Format
                possible_ip = possible_ip.split(',')[0]
            try:
                ip_addr = ip_address(possible_ip)
            except ValueError:
                # IP address isn't valid, keep checking headers
                continue
            # Ensure IP address isn't private or otherwise reserved
            if ip_addr.is_multicast or ip_addr.is_private or ip_addr.is_unspecified or\
                    ip_addr.is_reserved or ip_addr.is_loopback or ip_addr.is_link_local:
                # IP address isn't valid, keep checking headers
                continue

            if ip_addr:
                # IP address is valid this far, consider it valid
                break

    if ip_addr is None:
        # try to get from remote_addr
        possible_ip = request.remote_addr

        try:
            ip_addr = ip_address(possible_ip)
        except ValueError:
            return None # Can't find IP

    return ip_addr
