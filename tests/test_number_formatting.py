"""
Test number formatting
"""
from decimal import Decimal

import pytest
from quart import Quart

from quart_babel import (
    Babel,
    format_number,
    format_decimal,
    format_currency,
    format_percent,
    format_scientific
    )


@pytest.mark.asyncio
async def test_basic_numbers(app: Quart) -> None:
    """
    Test number formatting.
    """
    @app.route('/number')
    async def number() -> str:
        return format_number(1099)

    @app.route('/decimal')
    async def decimal() -> str:
        return format_decimal(Decimal(1010.99))

    @app.route('/currency')
    async def currency() -> str:
        return format_currency(1099, 'USD')

    @app.route('/percent')
    async def percent() -> str:
        return format_percent(0.19)

    @app.route('/scientific')
    async def scientific() -> str:
        return format_scientific(10000)

    Babel(app)

    client = app.test_client()

    res = await client.get('/number')
    assert await res.get_data(as_text=True) == '1,099'

    res = await client.get('/decimal')
    assert await res.get_data(as_text=True) == '1,010.99'

    res = await client.get('/currency')
    assert await res.get_data(as_text=True) == '$1,099.00'

    res = await client.get('/percent')
    assert await res.get_data(as_text=True) == '19%'

    res = await client.get('/scientific')
    assert await res.get_data(as_text=True) == '1E4'
