"""
tests.test_date_formatting
"""
from datetime import datetime, timedelta

import pytest
import quart

import quart_babel as babel
from quart_babel.utils import get_babel


@pytest.mark.asyncio
async def test_basic() -> None:
    """
    Test basic date formatting.
    """
    app = quart.Quart(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    delta = timedelta(days=6)

    async with app.test_request_context("/"):
        assert babel.format_datetime(d) == "Apr 12, 2010, 1:46:00\u202fPM"
        assert babel.format_date(d) == "Apr 12, 2010"
        assert babel.format_time(d) == "1:46:00\u202fPM"
        assert babel.format_timedelta(delta) == "1 week"
        assert babel.format_timedelta(delta, threshold=1) == "6 days"

    async with app.test_request_context("/"):
        get_babel(app).default_timezone = "Europe/Vienna"
        assert babel.format_datetime(d) == "Apr 12, 2010, 3:46:00\u202fPM"
        assert babel.format_date(d) == "Apr 12, 2010"
        assert babel.format_time(d) == "3:46:00\u202fPM"

    async with app.test_request_context("/"):
        get_babel(app).default_locale = "de_DE"
        assert babel.format_datetime(d, "long") == "12. April 2010, 15:46:00 MESZ"


@pytest.mark.asyncio
async def test_custom_formats() -> None:
    """
    Test custom formats.
    """
    app = quart.Quart(__name__)
    app.config.update(
        BABEL_DEFAULT_LOCALE="en_US", BABEL_DEFAULT_TIMEZONE="Pacific/Johnston"
    )

    b = babel.Babel(app)
    b.date_formats["datetime"] = "long"
    b.date_formats["datetime.long"] = "MMMM d, yyyy h:mm:ss a"
    d = datetime(2010, 4, 12, 13, 46)

    async with app.test_request_context("/"):
        assert babel.format_datetime(d) == "April 12, 2010 3:46:00 AM"


@pytest.mark.asyncio
async def test_custom_locale_selector() -> None:
    """
    Test custom locale selector
    """
    app = quart.Quart(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)

    the_timezone = "UTC"
    the_locale = "en_US"

    def locale_selector() -> str:
        return the_locale

    def timezone_selector() -> str:
        return the_timezone

    get_babel(app).locale_selector = locale_selector
    get_babel(app).timezone_selector = timezone_selector

    async with app.test_request_context("/"):
        assert babel.format_datetime(d) == "Apr 12, 2010, 1:46:00\u202fPM"

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    async with app.test_request_context("/"):
        assert babel.format_datetime(d) == "12.04.2010, 15:46:00"


@pytest.mark.asyncio
async def test_refreshing() -> None:
    """
    Test locale refreshing.
    """
    app = quart.Quart(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)

    async with app.test_request_context("/"):
        assert babel.format_datetime(d) == "Apr 12, 2010, 1:46:00\u202fPM"
        get_babel(app).default_timezone = "Europe/Vienna"
        babel.refresh()
        assert babel.format_datetime(d) == "Apr 12, 2010, 3:46:00\u202fPM"
