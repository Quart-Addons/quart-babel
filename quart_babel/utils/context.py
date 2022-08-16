"""
quart_babel.utils.context

This module provides utils for determining
the app context.
"""
from __future__ import annotations
from contextlib import contextmanager
from typing import Optional, TYPE_CHECKING
from quart import current_app, has_request_context, Quart, request, Request

if TYPE_CHECKING:
    from quart_babel.core import _BabelState

def get_state(app: Optional[Quart]=None, silent: bool=False) -> Optional[_BabelState]:
    """Gets the application-specific babel data.
    :param app: The Quart application. Defaults to the current app.
    :param silent: If set to True, it will return ``None`` instead of raising
                   a ``RuntimeError``.
    """
    if app is None:
        app = current_app

    if silent and (not app or 'babel' not in app.extensions):
        return None

    if 'babel' not in app.extensions:
        raise RuntimeError("The babel extension was not registered to the "
                           "current application. Please make sure to call "
                           "init_app() first.")

    return app.extensions['babel']

def refresh() -> None:
    """Refreshes the cached timezones and locale information.  This can
    be used to switch a translation between a request and if you want
    the changes to take place immediately, not just with the next request::

        user.timezone = request.form['timezone']
        user.locale = request.form['locale']
        refresh()
        flash(gettext('Language was changed'))

    Without that refresh, the :func:`~flask.flash` function would probably
    return English text and a now German page.
    """
    ctx = _get_current_context()
    for key in ('babel_locale', 'babel_tzinfo'):
        if hasattr(ctx, key):
            delattr(ctx, key)

@contextmanager
def force_locale(locale) -> None:
    """Temporarily overrides the currently selected locale.
    Sometimes it is useful to switch the current locale to
    different one, do some tasks and then revert back to the
    original one. For example, if the user uses German on the
    web site, but you want to send them an email in English,
    you can use this function as a context manager::

        with force_locale('en_US'):
            end_email(gettext('Hello!'), ...)

    :param locale: The locale to temporary switch to (ex: 'en_US').
    """
    ctx = _get_current_context()
    if ctx is None:
        yield
        return

    state: _BabelState = get_state()

    orig_locale_selector_func = state.babel.locale_selector_func
    orig_attrs = {}
    for key in ('babel_translations', 'babel_locale'):
        orig_attrs[key] = getattr(ctx, key, None)

    try:
        state.babel.locale_selector_func = lambda: locale
        for key in orig_attrs:
            setattr(ctx, key, None)
        yield
    finally:
        state.babel.locale_selector_func = orig_locale_selector_func
        for key, value in orig_attrs.items():
            setattr(ctx, key, value)

def _get_current_context() -> Request | Quart | None:
    """Returns the current request."""
    if has_request_context():
        return request

    if current_app:
        return current_app
