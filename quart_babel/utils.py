"""
quart_babel.utls

Utilites for Quart-Babel.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from ipaddress import ip_address
import re
import typing as t

from babel import Locale
from babel.dates import get_timezone as babel_get_timezone
from quart import current_app

from .typing import ASGIRequest, BaseTzInfo, ParsedHeader

if t.TYPE_CHECKING:
    from quart import Quart
    from .core import Babel
    from .domain import Domain

__all__ = (
    'BabelState',
    'get_state',
    'convert_locale',
    'convert_timezone',
    'parse_accept_header',
    'get_ip_address'
)

@dataclass
class BabelState:
    """
    This class holds the state of `quart_babel`
    within the application.

    Part of the internal API.

    Arguments:
        babel: The :class:`Babel` instance.
        app: The quart application.
        domain: The :class:`Domain` instance.
        locale_cache: Dictionary of cached locales. On
            construction this is an empty dictionary.
    """
    babel: Babel
    app: Quart
    domain: Domain
    locale_cache: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f'<BabelState({self.babel}, {self.app}, {self.domain})>'

def get_state(app: Quart | None = None, silent: bool = False) -> BabelState | None:
    """
    Gets the babel data for the application.

    Part of the internal API.

    Arguments:
        app: The application. If not passed to the function, then defaults to the `current_app`.
        silent: If set to ``True``, it will return ``None`` instead of raising a `RuntimeError`.
    """
    if app is None:
        app = current_app

    if silent and (not app or 'babel' not in app.extensions):
        return None

    if 'babel' not in app.extensions:
        raise RuntimeError(
            "The babel extension was not registered to the "
            "the current application. Please make sure to call "
            "init_app first."
        )

    return app.extensions['babel']

def convert_locale(locale: Locale | str) -> Locale:
    """
    Convert the locale to a `babel.Locale` object.

    It will also determine the seperator type used for the
    given locale passed to the function and will then use it
    for `babel.Locale.parse`.

    Part of the internal API.

    Arguments:
        locale: The locale to convert.
    """
    if isinstance(locale, str):
        # Get seperatir from `locale` argument.
        if len(locale) > 2:
            sep = str(locale)[2]
            return Locale.parse(locale, sep=sep)
        else:
            return Locale.parse(locale)
    return locale

def convert_timezone(zone: BaseTzInfo | str) -> BaseTzInfo:
    """
    Converts the timezone as a `pytz.BaseTzInfo` object.

    Part of the internal API.

    Arguments:
        zone: The timezone to get.
    """
    if isinstance(zone, str):
        return babel_get_timezone(zone)
    return zone

def parse_accept_header(header: str) -> ParsedHeader:
    """
    Parse accept headers.

    Part of the internal API.

    Arguments:
        headers: The accept header to parse.
    """
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

def get_ip_address(request: ASGIRequest):
    """
    Makes the best attempt to get the client's real IP address or return.

    Part of the internal API.

    Arguments:
        request: The ASGI App request object.
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
