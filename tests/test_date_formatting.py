"""
Tests date and time formatting
with Quart Babel.
"""
import asyncio
from datetime import datetime, timedelta
from time import time
import pytest

from quart import Quart
from quart_babel import (Babel, format_date, format_datetime, format_timedelta,
                        refresh, force_locale, get_locale)
from quart_babel.utils.formats import _get_format

@pytest.mark.asyncio
async def test_basic():
    """
    Tests basic functions for
    date and time functions.
    """
    app = Quart(__name__)
    Babel(app)

    date = datetime(2022, 8, 8, 17, 46)
    delta = timedelta(days=6)

    async with app.test_request_context("/"):
        assert format_datetime(date) == 'Aug 8, 2022, 5:46:00 PM'
        assert format_date(date) == 'Aug 8, 2022'
        assert time(date) == '5:46:00 PM'
        assert format_timedelta(delta, threshold=1) == '6 days'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europene/Vienna'
        assert format_datetime(date) == 'Aug 8, 2022, 11:46:00 PM'
        assert format_date(date) == 'Aug 8, 2022'
        assert time(date) == '11:46:00 PM'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE'
        assert format_datetime(date, 'long') == \
            '8. Aug 8 um 2022, 23:46:00 MESZ'

@pytest.mark.asyncio
async def test_init_app():
    """
    Tests basic functions for
    date and time functions using
    `quart_babel.init_app`.
    """
    babel = Babel()
    app = Quart(__name__)
    babel.init_app(app)

    date = datetime(2022, 8, 8, 17, 46)

    async with app.test_request_context("/"):
        assert format_datetime(date) == 'Aug 8, 2022, 5:46:00 PM'
        assert format_date(date) == 'Aug 8, 2022'
        assert time(date) == '5:46:00 PM'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europene/Vienna'
        assert format_datetime(date) == 'Aug 8, 2022, 11:46:00 PM'
        assert format_date(date) == 'Aug 8, 2022'
        assert time(date) == '11:46:00 PM'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE'
        assert format_datetime(date, 'long') == \
            '8. Aug 8 um 2022, 23:46:00 MESZ'

@pytest.mark.asyncio
async def test_custom_formates():
    """
    Tests custom date and time formats.
    """
    app = Quart(__name__)
    app.config.update(
        BABEL_DEFAULT_LOCALE='en_us',
        BABEL_DEFAULT_TIMEZONE='Pacific/Johnston'
    )
    babel = Babel(app)
    babel.date_formats['datetime'] = 'long'
    babel.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'

    babel.date_formats['date'] = 'long'
    babel.date_formats['short'] = 'MM d'

    date = datetime(2022, 8, 8, 17, 46)

    async with app.test_request_context("/"):
        assert format_datetime(date) == 'August 8, 2022 5:46:00 PM'
        assert _get_format('datetime') == 'MMMM d, yyyy h:mm:ss a'
        # none, returns the format
        assert _get_format('datetime', 'medium') == 'medium'
        assert _get_format('date', 'short') == 'MM d'

@pytest.mark.asyncio
async def test_custom_locale_selector():
    """
    Tests a custom locale selector.
    """
    app = Quart(__name__)
    babel = Babel(app)

    date = datetime(2022, 8, 8, 17, 46)

    the_locale = 'en_US'
    the_timezone = 'UTC'

    @babel.localeselector
    def select_locale():
        return the_locale

    @babel.timezoneselector
    def select_timezone():
        return the_timezone

    async with app.test_request_context("/"):
        assert format_datetime(date) == 'Aug 8, 2022, 5:46 PM'

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    async with app.test_request_context("/"):
        assert format_datetime(date) == '08.08.2022, 17:46:00'

@pytest.mark.asyncio
async def test_async_custom_locale_selector():
    """
    Tests a custom locale selector that is async.
    """
    app = Quart(__name__)
    babel = Babel(app)

    date = datetime(2022, 8, 8, 17, 46)

    the_locale = 'en_US'
    the_timezone = 'UTC'

    @babel.localeselector
    async def select_locale():
        await asyncio.sleep(0.1)
        return the_locale

    @babel.timezoneselector
    async def select_timezone():
        await asyncio.sleep(0.2)
        return the_timezone

    async with app.test_request_context("/"):
        assert format_datetime(date) == 'Aug 8, 2022, 5:46 PM'

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    async with app.test_request_context("/"):
        assert format_datetime(date) == '08.08.2022, 17:46:00'

@pytest.mark.asyncio
async def test_refreshing():
    """
    Test Quart Babel refreshing.
    """
    app = Quart(__name__)
    Babel(app)

    date = datetime(2022, 8, 8, 17, 46)

    refresh() # nothing shoule be refreshed (see case below)

    async with app.test_request_context("/"):
        assert format_datetime(date) == 'Aug 8, 2022, 5:46:00 PM'
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
        refresh()
        assert format_datetime(date) == 'Aug 8, 2022, 11:46:00 PM'

@pytest.mark.asyncio
async def test_force_locale():
    """
    Tests forcing the locale.
    """
    app = Quart(__name__)
    babel = Babel(app)

    @babel.localeselector
    def select_locale():
        return 'de_DE'

    with force_locale('en_US'):
        assert get_locale() is None

    async with app.test_request_context("/"):
        assert str(get_locale()) == 'de_DE'

        with force_locale('en_US'):
            assert str(get_locale()) == 'en_US'

        assert str(get_locale()) == 'de_DE'
