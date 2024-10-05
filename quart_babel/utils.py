"""
quart_babel.utils
"""
from __future__ import annotations
from types import SimpleNamespace
from typing import Optional, TYPE_CHECKING

from quart import Quart, current_app, g

if TYPE_CHECKING:
    from .core import BabelConfiguration


def get_babel(app: Optional[Quart] = None) -> BabelConfiguration:
    """
    Returns the `BabelConfiguration` from the application.
    """
    if app is None:
        app = current_app
    return app.extensions["babel"]


def _get_current_context() -> Optional[SimpleNamespace]:
    if not g:
        return None

    if not hasattr(g, "_quart_babel"):
        g._quart_babel = SimpleNamespace()  # pylint: disable=W0212

    return g._quart_babel  # pylint: disable=W0212


def refresh() -> None:
    """
    Refreshes the cached timezones and locale information.  This can
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

    for key in "babel_locale", "babel_tzinfo", "babel_translations":
        if hasattr(ctx, key):
            delattr(ctx, key)

    if hasattr(ctx, "forced_babel_locale"):
        ctx.babel_locale = ctx.forced_babel_locale
