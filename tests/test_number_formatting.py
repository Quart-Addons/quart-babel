"""
tests.test_number_formatting
"""
from decimal import Decimal

import pytest
import quart
import quart_babel as babel


@pytest.mark.asyncio
async def test_basics() -> None:
    """
    Test basic number formatting.
    """
    app = quart.Quart(__name__)
    babel.Babel(app)
    n = 1099

    async with app.test_request_context("/"):
        assert babel.format_number(n) == "1,099"
        assert babel.format_decimal(Decimal("1010.99")) == "1,010.99"
        assert babel.format_currency(n, "USD") == "$1,099.00"
        assert babel.format_percent(0.19) == "19%"
        assert babel.format_scientific(10000) == "1E4"
