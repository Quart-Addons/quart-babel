"""
Tests date formatting.
"""
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import pytest

import quart_babel as babel_ext
from quart_babel.utils.context import get_state
from quart_babel.utils.formats import _get_format

@pytest.mark.asyncio
async def test_date_formatting_basic(app, babel):
    d= datetime(2010, 4, 12, 13, 46)
    delta = timedelta(days=6)

    async with app.test_request_context("/"):
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
        assert babel.format_date(d) == 'Apr 12, 2010'
        assert babel.format_time(d) == '1:46:00 PM'
        assert babel.format_timedelta(delta) == '1 week'
        assert babel.format_timedelta(delta, threshold=1) == '6 days'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
        assert babel.format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
        assert babel.format_date(d) == 'Apr 12, 2010'
        assert babel.format_time(d) == '3:46:00 PM'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE'
        assert babel.format_datetime(d, 'long') == \
            '12. April 2010 um 15:46:00 MESZ'

@pytest.mark.asyncio
async def test_date_formatting_init_app(app):
    babel = babel_ext.Babel()
    babel.init_app(app)
    d = datetime(2010, 4, 12, 13, 46)

    async with app.test_request_context("/"):
        assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
        assert babel_ext.format_date(d) == 'Apr 12, 2010'
        assert babel_ext.format_time(d) == '1:46:00 PM'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
        assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
        assert babel_ext.format_date(d) == 'Apr 12, 2010'
        assert babel_ext.format_time(d) == '3:46:00 PM'

    async with app.test_request_context("/"):
        app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE'
        assert babel_ext.format_datetime(d, 'long') == \
            '12. April 2010 um 15:46:00 MESZ'

@pytest.mark.asyncio
async def test_date_formatting_custom_formats(app):
    app.config.update(
            BABEL_DEFAULT_LOCALE='en_US',
            BABEL_DEFAULT_TIMEZONE='Pacific/Johnston'
        )
    babel = babel_ext.Babel(app)
    babel.date_formats['datetime'] = 'long'
    babel.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'
    babel.date_formats['date'] = 'long'
    babel.date_formats['date.short'] = 'MM d'
    d = datetime(2010, 4, 12, 13, 46)

    async with app.test_request_context("/"):
        assert babel_ext.format_datetime(d) == 'April 12, 2010 3:46:00 AM'
        assert _get_format('datetime') == 'MMMM d, yyyy h:mm:ss a'
        # none; returns the format
        assert _get_format('datetime', 'medium') == 'medium'
        assert _get_format('date', 'short') == 'MM d'

@pytest.mark.asyncio
async def test_date_formatting_custom_locale_selector(app):
    app = quart.Quart(__name__)
    babel = babel_ext.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    the_timezone = 'UTC'
    the_locale = 'en_US'

    @babel.localeselector
    def select_locale():
        return the_locale

    @babel.timezoneselector
    def select_timezone():
        return the_timezone

    async with app.test_request_context("/"):
        assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    async with app.test_request_context("/"):
        assert babel_ext.format_datetime(d) == '12.04.2010, 15:46:00'

@pytest.mark.asyncio
async def test_date_formatting_async_custom_locale_selector(app):
    app = quart.Quart(__name__)
    babel = babel_ext.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    the_timezone = 'UTC'
    the_locale = 'en_US'

    @babel.localeselector
    async def select_locale():
        asyncio.sleep(0.1)
        return the_locale

    @babel.timezoneselector
    async def select_timezone():
        asyncio.sleep(0.2)
        return the_timezone

    async with app.test_request_context("/"):
        assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    async with app.test_request_context("/"):
        assert babel_ext.format_datetime(d) == '12.04.2010, 15:46:00'