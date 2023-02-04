"""
quart_babel.middleware

Provides middleware for Babel to use with `Quart`.
"""
from asgi_tools import Request

from .locale import setup_locale_context, set_locale, select_locale_by_request
from .timezone import setup_timezone_context, set_timezone, select_timezone_by_request

from .typing import (
    ASGIApp,
    ASGIRequest,
    Receive,
    Scope,
    Send,
    LocaleSelectorFunc,
    TimezoneSelectorFunc
)

class QuartBabelMiddleware:
    """
    Babel Middleware to be used with `quart.Quart` to determine the
    locale and timezone using custom selector functions or using the
    ASGI Request.

    The need for this function is so the locale and timezone detection
    can be async and allows Quart Babel to be used by other extensions.
    """
    def __init__(
        self,
        app: ASGIApp,
        default_locale: str,
        locale_selector: LocaleSelectorFunc | None,
        default_timezone: str,
        ipapi_key: str | None,
        timezone_selector: TimezoneSelectorFunc | None
        ) -> None:
        """
        Construct an instance of the class.

        Attributes:
            app: ASGI Application.
            default_locale: The default locale to use.
            locale_selector: Custom locale selector function.
            default_timezone: The default timezone to use.
            ipapi_key: The IP API key to use.
            timezone_selector: Custom timezone selector function.
        """
        self.app = app

        self.default_locale = default_locale
        self.locale_selector = locale_selector

        self.default_timezone = default_timezone
        self.ipapi_key = ipapi_key
        self.timezone_selector = timezone_selector

        setup_locale_context(self.default_locale)
        setup_timezone_context(self.default_timezone)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> ASGIApp:
        """
        This method will be called by the ASGI app to determine the users locale or
        timezone by using methods :func:`QuartBabelMiddleware.detect_locale` and
        :func:`QuartBabelMiddleware.det_timezone`.

        Arguments:
            scope: The ASGI scope.
            recieve: The ASGI recieve object.
            send: the ASGI send object.
        """
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)

        if isinstance(scope, Request):
            request = scope
        else:
            request = Request(scope)

        await self.detect_locale(request)
        await self.detect_timezone(request)

        return await self.app(scope, receive, send)

    async def detect_locale(self, request: ASGIRequest) -> None:
        """
        Detect the locale by using the custom locale selector
        function. If there is no custom locale selector function
        then the locale will be determined by the request (scope)
        using the :func:`quart_babel.select_locale_by_request` function.

        Arguments:
            request: ASGI Request object.
        """
        if self.locale_selector is not None:
            lang = await self.locale_selector(request)
        else:
            lang = await select_locale_by_request(request)

        if lang is None:
            lang = self.default_locale

        set_locale(lang)

    async def detect_timezone(self, request: ASGIRequest) -> None:
        """
        Detect the timezone by using the custom timezone selector
        function. If there is no custom timezone selector function
        then the timezone will be determined by the request (scope)
        using the :func:`quart_babel.select_timezone_by_request` function.

        Arguments:
            request (`ASGIRequest`): ASGI Request object.
        """
        if self.timezone_selector is not None:
            tz_info = await self.timezone_selector(request, self.ipapi_key)
        else:
            tz_info = await select_timezone_by_request(request, self.ipapi_key)

        if tz_info is None:
            tz_info = self.default_timezone

        set_timezone(tz_info)
  