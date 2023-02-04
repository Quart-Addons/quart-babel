"""
quart_babel.typing

Provides custom typing for Quart Babel.
"""
from typing import (
    Awaitable,
    Callable,
    Iterator,
    Literal,
    NewType,
    Optional,
    Tuple,
    Union
)

from pytz import BaseTzInfo as _BaseTzInfo
from asgi_tools import Request

from babel import Locale as _Locale, support

from hypercorn.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    Scope as _Scope
)

# ASGI TYPES - Used for Middleware and/or Selector Functions.
ASGIRequest = Request
Receive = ASGIReceiveCallable
Scope = _Scope
Send = ASGISendCallable
ASGIApp = Callable[[Scope, Receive, Send], Awaitable]

# LOCALE TYPES - Types for Babel Locales, etc.
Locale = _Locale
LocaleSelectorFunc = Callable[[ASGIRequest], Awaitable[Optional[str]]]
ParsedHeader = Iterator[Tuple[float, str]]
Translations = Union[support.Translations, support.NullTranslations]

# TIMEZONE TYPES - Types used for Timezones.
BaseTzInfo = _BaseTzInfo
IPApiKey = NewType("IPApiKey", str)
TimezoneSelectorFunc = Callable[[ASGIRequest, Optional[IPApiKey]], Awaitable[Optional[str]]]

# DATETIME TYPES
DateTimeFormats = Literal["short", "medium", "long", "full"]

TimeDeltaFormats = Literal["narrow", "short", "long"]

Granularity = Literal["year", "month", "week", "day", "hour", "minute", "second"]
