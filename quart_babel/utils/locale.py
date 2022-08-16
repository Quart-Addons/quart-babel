"""
quart_babel.utils.locale

This module provides utils for determining
the user locale.
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING, Iterator, Optional, Tuple
from babel import Locale
from quart import request
from quart.utils import is_coroutine_function, run_sync

from .context import get_state, _get_current_context

if TYPE_CHECKING:
    from quart_babel.core import _BabelState

async def get_locale() -> Optional[Locale]:
    """Returns the locale that should be used for this request as
    `babel.Locale` object. This reutnrs `None` if used outside of
    a request.
    """
    ctx = _get_current_context()

    if ctx is None:
        # outside of an request context.
        return None

    locale = getattr(ctx, 'babel_locale', None)
    state: _BabelState = get_state()

    # no locale found on current request context
    if locale is None:
        if state.babel.locale_selector_func is not None:
            if is_coroutine_function(state.babel.locale_selector_func):
                result = await state.babel.locale_selector_func()
            else:
                result = await run_sync(state.babel.locale_selector_func)()

            locale = state.babel.load_locale(result)
        else:
            locale = state.babel.default_locale

        # set the local for the current request
        ctx.babel_locale = locale

    return locale

async def select_locale_by_request() -> Optional[str]:
    """
    Select a locale by a given request.
    """
    locale_header = request.headers.get("accept-language")
    if locale_header:
        ulocales = list(_parse_accept_header(locale_header))
        if ulocales:
            return ulocales[0][1]
    return None

def _parse_accept_header(header: str) -> Iterator[Tuple[float, str]]:
    """Parse accept headers."""
    result = []
    for match in _accept_re.finditer(header):
        quality = 1.0
        try:
            if match.group(2):
                quality = max(min(float(match.group(2)), 1), 0)
            if match.group(1) == "*":
                continue
        except ValueError:
            continue
        result.append((quality, match.group(1)))

    return reversed(sorted(result))

_locale_delim_re = re.compile(r"[_-]")

_accept_re = re.compile(
    r"""(                         # media-range capturing-parenthesis
            [^\s;,]+              # type/subtype
            (?:[ \t]*;[ \t]*      # ";"
            (?:                   # parameter non-capturing-parenthesis
                [^\s;,q][^\s;,]*  # token that doesn't start with "q"
            |                     # or
                q[^\s;,=][^\s;,]* # token that is more than just "q"
            )
            )*                    # zero or more parameters
        )                         # end of media-range
        (?:[ \t]*;[ \t]*q=        # weight is a "q" parameter
            (\d*(?:\.\d+)?)       # qvalue capturing-parentheses
            [^,]*                 # "extension" accept params: who cares?
        )?                        # accept params are optional
    """,
    re.VERBOSE,
)
