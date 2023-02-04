"""
quart_babel.locales

Provides helpers for the Babel locale.
"""
from contextlib import contextmanager
import typing as t

from .context import LocaleStorageContext
from .typing import ASGIRequest, Locale
from .utils import convert_locale, parse_accept_header

__all__ = (
    'setup_locale_context',
    'get_locale',
    'set_locale',
    'switch_locale',
    'refresh_locale',
    'select_locale_by_request'
)

_current_locale = LocaleStorageContext()

def setup_locale_context(default_locale: Locale | str) -> None:
    """
     Setups context with the default locale value using
    `LocaleStorageContext.setup_context` method.

    Arguments:
        default_locale: The default locale to use.
    """
    _current_locale.setup_context(default_locale)

def get_locale() -> Locale | None:
    """
    Gets the current active locale from context.
    """
    return _current_locale.get()

def set_locale(locale: Locale | str) -> None:
    """
    Sets the active locale to context.

    Part of the internal API.

    Arguments:
        locale: The locale to set.
    """
    locale = convert_locale(locale)
    _current_locale.set(locale)

@contextmanager
def switch_locale(locale: str) -> t.Generator[None, None, None]:
    """
    Temporary switch current locale for a code block. The previous
    locale will be restored after exiting the manager.

    Use example:
        with switch_locale('en-US'):
                end_email(gettext('Hello!'), ...)

    Arguments:
        locale: The locale to temporary switch to (ex: 'en_US').
    """
    old_locale = get_locale()
    set_locale(locale)
    yield
    set_locale(old_locale)

def refresh_locale(locale: str | None = None) -> None:
    """
    Refreshes the cached locale information. This can be used
    to switch a translation between a request and if you want
    the changes to take place immediately, not just with the
    next request.

    Arguments:
    locale: The locale to set. If none is used it will use the default
        locale.
    """
    _current_locale.refresh(locale)

async def select_locale_by_request(request: ASGIRequest) -> str | None:
    """
    Gets the users locale by a given request.

    Arguments:
        request: The ASGI Request object.
    """
    locale_header = request.headers.get("accept-language")

    if locale_header:
        ulocales = list(parse_accept_header(locale_header))
        if ulocales:
            return ulocales[0][1]
    return None
