"""
Test middleware and helpers used for Quart-Babel.
"""
from __future__ import annotations
import asyncio
import typing as t

import pytest
import asgi_tools as tools

from quart_babel import gettext, select_locale_by_request
from quart_babel.typing import ASGIRequest

if t.TYPE_CHECKING:
    from quart import Quart
    from quart_babel import Babel


@pytest.mark.asyncio
async def test_select_locale_by_request() -> None:
    """
    Test the select locale by request function.
    """
    request = tools.Request(
        {
            "headers": [
                (b"accept-language", b"fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5")  # noqa: E501
            ]
        },
        None,
        None
    )

    lang = await select_locale_by_request(request)
    assert lang == 'fr-CH'

    request = tools.Request(
        {
            "headers": [
                (b"accept-language", b"en-US,en;q=0.9,ru;q=0.8,ru-RU;q=0.7")
            ]
        },
        None,
        None
    )

    lang = await select_locale_by_request(request)
    assert lang == 'en-US'


@pytest.mark.asyncio
async def test_middleware_locale(app: Quart, babel: Babel) -> None:
    """
    Test Quart Babel Middleware to detect locale.
    """
    @app.route('/hello')
    async def hello() -> str:
        return gettext('Hello World!')

    babel(app)
    client = app.test_client()

    res = await client.get('/locale')
    assert await res.get_data(as_text=True) == 'en'

    res = await client.get(
        '/locale', headers={'accept-language': 'fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5'}  # noqa: E501
        )
    assert await res.get_data(as_text=True) == 'fr'

    res = await client.get('/hello')
    assert await res.get_data(as_text=True) == 'Hello World!'

    res = await client.get(
        '/hello', headers={'accept-language': 'fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5'}  # noqa: E501
        )
    assert await res.get_data(as_text=True) == 'Bonjour le monde!'


@pytest.mark.asyncio
async def test_custom_locale_selector(app: Quart, babel: Babel) -> None:
    """
    Test custom locale selector function.
    """
    @app.route('/hello')
    async def hello() -> str:
        return gettext('Hello World!')

    async def custom_locale(request: ASGIRequest) -> str:
        await asyncio.sleep(0.1)
        return 'fr-CH'

    babel = babel()
    babel.locale_selector = custom_locale
    babel.init_app(app)
    client = app.test_client()

    res = await client.get('/locale')
    assert await res.get_data(as_text=True) == 'fr'

    res = await client.get('/hello')
    assert await res.get_data(as_text=True) == 'Bonjour le monde!'


@pytest.mark.asyncio
async def test_custom_timezone_selector(app: Quart, babel: Babel) -> None:
    """
    Test custom timezone selector function.
    """
    async def custom_timezone(request: ASGIRequest) -> str:
        await asyncio.sleep(0.2)
        return 'America/Los_Angeles'

    babel = babel()
    babel.timezone_selector = custom_timezone
    babel.init_app(app)
    client = app.test_client()

    res = await client.get('/zone')
    assert await res.get_data(as_text=True) == 'America/Los_Angeles'
