"""
Test number formatting
"""
from decimal import Decimal
import pytest

from quart import Quart
from quart_babel import (Babel, format_number, format_decimal, format_currency,
                        format_percent, format_scientific)

@pytest.mark.asyncio
async def test_basic_numbers():
    """
    Test number formatting.
    """
    app = Quart(__name__)
    Babel(app)

    number = 1099
    dec_number = 1010.99
    p_num = 0.19
    sci_number = 10000

    async with app.test_request_context("/"):
        assert format_number(number) == '1,099'
        assert format_decimal(Decimal(dec_number)) == '1,010.99'
        assert format_currency(number, 'USD') == '$1,099.00'
        assert format_percent(p_num) == '19%'
        assert format_scientific(sci_number) == '1E4'
