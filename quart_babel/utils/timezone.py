"""
quart_babel.utils.timezone

This module provides utils for determining
the user timezone.
"""
import typing as t
from ipaddress import ip_address
from urllib.parse import unquote

import ipapi
from pytz import timezone, UTC
from quart import current_app, request

from .awaitable import _is_awaitable, _run_async
from .context import get_state, _get_current_context
from .typing import BabelState

def get_timezone():
    """Returns the timezone that should be used for this request as
    `pytz.timezone` object.  This returns `None` if used outside of
    a request.
    """
    ctx = _get_current_context()
    if ctx is None:
        # outside of an request context
        return None

    tzinfo = getattr(ctx, 'babel_tzinfo', None)
    state: BabelState = get_state()
    if tzinfo is None:
        if state.babel.timezone_selector_func is not None:
            if _is_awaitable(state.babel.timezone_selector_func()):
                return_val = _run_async(state.babel.timezone_selector_func())
            else:
                return_val = state.babel.timezone_selector_func()

            if return_val is None:
                return_val = select_timezone_by_request()

                if return_val is None:
                    tzinfo = state.babel.default_timezone
                else:
                    if isinstance(return_val, str):
                        tzinfo = timezone(return_val)
                    else:
                        tzinfo = return_val
            else:
                if isinstance(return_val, str):
                    tzinfo = timezone(return_val)
                else:
                    tzinfo = return_val
        else:
            return_val = select_timezone_by_request()

            if return_val is None:
                tzinfo = state.babel.default_timezone
            else:
                if isinstance(return_val, str):
                    tzinfo = timezone(return_val)
                else:
                    tzinfo = return_val

        ctx.babel_tzinfo = tzinfo
    return tzinfo

def select_timezone_by_request() -> t.Optional[str]:
    """
    Select the timezone by a given request.
    """
    tzone = None
    tzone = request.cookies.get('timezone', None)

    if tzone:
        tzone = unquote(timezone)
    else:
        ipapi_key = current_app.config.get('BABEL_IPAPI_KEY', None)
        ip = _get_ip_address()
        ip_info = ipapi.location(ip, ipapi_key)
        tzone = ip_info.get('timezone', None)

    return tzone

def to_user_timezone(datetime):
    """Convert a datetime object to the user's timezone.  This automatically
    happens on all date formatting unless rebasing is disabled.  If you need
    to convert a :class:`datetime.datetime` object at any time to the user's
    timezone (as returned by :func:`get_timezone` this function can be used).
    """
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=UTC)
    tzinfo = get_timezone()
    return tzinfo.normalize(datetime.astimezone(tzinfo))

def to_utc(datetime):
    """Convert a datetime object to UTC and drop tzinfo.  This is the
    opposite operation to :func:`to_user_timezone`.
    """
    if datetime.tzinfo is None:
        datetime = get_timezone().localize(datetime)
    return datetime.astimezone(UTC).replace(tzinfo=None)

def _get_ip_address():
    """ Makes the best attempt to get the client's real IP
    or return the loopback.
    :param request Request: The request object from the middleware.
    """
    POSSIBLE_HEADERS = [
        'HTTP_X_FORWARDED_FOR', 'HTTP_FORWARDED'
        'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR'
    ]
    ip = ''
    for header in POSSIBLE_HEADERS:
        possible_ip = request.META.get(header)
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
                ip = ip_address(possible_ip)
            except ValueError:
                # IP address isn't valid, keep checking headers
                continue
            # Ensure IP address isn't private or otherwise reserved
            if ip.is_multicast or ip.is_private or ip.is_unspecified or\
                    ip.is_reserved or ip.is_loopback or ip.is_link_local:
                # IP address isn't valid, keep checking headers
                continue

            if ip:
                # IP address is valid this far, consider it valid
                break

    return ip
