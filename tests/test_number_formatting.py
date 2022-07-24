"""
Tests number formatting.
"""
import pytest 
from decimal import Decimal

from quart import Quart
import quart_babel as babel_ext

@pytest.mark.asyncio
class NumberFormattingTestCase:

    async def test_basics(self):
        app = Quart(__name__)
        babel_ext.Babel(app)
        n = 1099

        async with app.test_request_context("/"):
            assert babel_ext.format_number(n) == '1,099'
            assert babel_ext.format_decimal(Decimal('1010.99')) == '1,010.99'
            assert babel_ext.format_currency(n, 'USD') == '$1,099.00'
            assert babel_ext.format_percent(0.19) == '19%'
            assert babel_ext.format_scientific(10000) == '1E4'
