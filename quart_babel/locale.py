"""
quart_babel.locale
"""
from __future__ import annotations
from contextlib import contextmanager
from typing import Any, Generator, Optional

from babel import Locale

from .utils import get_babel, _get_current_context


def get_locale() -> Optional[Locale]:
    """
    Returns the locale that should be used for
    this request as `babel.Locale` object.
    This returns `None` if used outside a request.
    """
    ctx = _get_current_context()

    if ctx is None:
        return None

    locale = getattr(ctx, "babel_locale", None)

    if locale is None:
        babel = get_babel()

        if babel.locale_selector is None:
            locale = babel.instance.default_locale
        else:
            rv = babel.locale_selector()

            if rv is None:
                locale = babel.instance.default_locale
            else:
                locale = Locale.parse(rv)

        ctx.babel_locale = locale

    return locale


@contextmanager
def force_locale(locale: str) -> Generator[None, Any, None]:
    """
    Temporarily overrides the currently selected locale.

    Sometimes it is useful to switch the current locale to different one, do
    some tasks and then revert back to the original one. For example, if the
    user uses German on the website, but you want to email them in English,
    you can use this function as a context manager::

        with force_locale('en_US'):
            send_email(gettext('Hello!'), ...)

    :param locale: The locale to temporary switch to (ex: 'en_US').
    """
    ctx = _get_current_context()

    if ctx is None:
        yield
        return

    orig_attrs = {}

    for key in ("babel_translations", "babel_locale"):
        orig_attrs[key] = getattr(ctx, key, None)

    try:
        ctx.babel_locale = Locale.parse(locale)
        ctx.forced_babel_locale = ctx.babel_locale
        ctx.babel_translations = None
        yield
    finally:
        if hasattr(ctx, "forced_babel_locale"):
            del ctx.forced_babel_locale

        for key, value in orig_attrs.items():
            setattr(ctx, key, value)
