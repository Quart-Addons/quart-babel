"""
Test date and time formatting with Quart-Babel.
"""
from __future__ import annotations
from datetime import datetime, timedelta

import pytest
from quart import Quart

from quart_babel import Babel
from quart_babel.formatters import _get_format
from quart_babel.typing import ASGIRequest


date = datetime(2010, 4, 12, 13, 46)
delta = timedelta(days=6)


@pytest.mark.asyncio
async def test_format_default(app: Quart) -> None:
    """
    Test basic formats using the default values.
    """
    async def timezone(request: ASGIRequest) -> str:
        return 'UTC'

    Babel(app, timezone_selector=timezone)

    client = app.test_client()

    res = await client.get('/datetime')
    assert await res.get_data(as_text=True) == 'Apr 12, 2010, 1:46:00\u202fPM'

    res = await client.get('/date')
    assert await res.get_data(as_text=True) == 'Apr 12, 2010'

    res = await client.get('/time')
    assert await res.get_data(as_text=True) == '1:46:00\u202fPM'

    res = await client.get('/timedelta')
    assert await res.get_data(as_text=True) == '6 days'


@pytest.mark.asyncio
async def test_format_vienna_tz(app: Quart) -> None:
    """
    Test basic formats using the Europe/Vienna timezone
    """
    async def timezone(request: ASGIRequest) -> str:
        return 'Europe/Vienna'

    babel = Babel()
    babel.init_app(app, timezone_selector=timezone)

    client = app.test_client()

    res = await client.get('/datetime')
    assert await res.get_data(as_text=True) == 'Apr 12, 2010, 3:46:00\u202fPM'

    res = await client.get('/date')
    assert await res.get_data(as_text=True) == 'Apr 12, 2010'

    res = await client.get('/time')
    assert await res.get_data(as_text=True) == '3:46:00\u202fPM'


@pytest.mark.asyncio
async def test_format_de(app: Quart) -> None:
    """
    Test basic formats using the Europe/Vienna timezone
    """
    async def locale(request: ASGIRequest) -> str:
        return 'de-DE'

    async def timezone(request: ASGIRequest) -> str:
        return 'Europe/Vienna'

    babel = Babel()
    babel.init_app(
        app, locale_selector=locale, timezone_selector=timezone
        )

    client = app.test_client()

    res = await client.get('/datetime/long')
    assert await res.get_data(as_text=True) == \
        '12. April 2010, 15:46:00 MESZ'


@pytest.mark.asyncio
async def test_custom_formats(app: Quart) -> None:
    """
    Test custom formats.
    """
    async def locale(request: ASGIRequest) -> str:
        return 'en-US'

    async def timezone(request: ASGIRequest) -> str:
        return 'Pacific/Johnston'

    babel = Babel(app, locale_selector=locale, timezone_selector=timezone)
    babel.date_formats['datetime'] = 'long'
    babel.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'
    babel.date_formats['date'] = 'long'
    babel.date_formats['date.short'] = 'MM d'

    client = app.test_client()

    res = await client.get('/datetime')
    assert await res.get_data(as_text=True) == 'April 12, 2010 3:46:00 AM'

    async with app.app_context():
        assert _get_format('datetime') == 'MMMM d, yyyy h:mm:ss a'
        # none, returns the format
        assert _get_format('datetime', 'medium') == 'medium'
        assert _get_format('date', 'short') == 'MM d'
