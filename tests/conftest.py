"""
Configure Pytest.
"""
from datetime import datetime, timedelta
import pytest

from quart import Quart

from quart_babel import (
    Babel,
    format_date,
    format_datetime,
    format_time,
    format_timedelta
)

from quart_babel.locale import get_locale
from quart_babel.timezone import get_timezone

date = datetime(2010, 4, 12, 13, 46)
delta = timedelta(days=6)

@pytest.fixture
def app() -> Quart:
    """
    Quart application for testing
    """
    app = Quart(__name__)

    @app.route('/locale')
    async def locale():
        return get_locale().language

    @app.route('/zone')
    async def zone():
        return str(get_timezone())

    @app.route('/datetime', defaults={'format': None})
    @app.route('/datetime/<format>')
    async def date_time(format: str | None):
        if format:
            return format_datetime(date, format)
        else:
            return format_datetime(date)

    @app.route('/date')
    async def date_format():
        return format_date(date)

    @app.route('/time')
    async def time():
        return format_time(date)

    @app.route('/timedelta')
    async def time_delta():
        return format_timedelta(delta, threshold=1)

    return app

@pytest.fixture
def babel() -> Babel:
    """
    Quart-Babel Extension for testing.
    """
    return Babel
