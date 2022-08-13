"""
Tests the core `quart_babel` integration.
"""
from datetime import datetime
import pytest
from babel import Locale
from pytz import timezone, UTC

from quart import Quart
from quart_babel import Babel, get_locale, get_timezone, to_utc, to_user_timezone
from quart_babel.utils.context import get_state

def test_configure_jinja():
    """
    Test `jinja` configuration in
    `quart_babel`.
    """
    app = Quart(__name__)
    Babel(app, configure_jinja=False)
    assert not app.jinja_env.filters.get("scientificformat")

@pytest.mark.asyncio
async def test_get_state():
    """
    Tests the `get_state` function.
    """
    # app = None, app.extensions = False, babel = False, silent = True
    assert get_state(silent=True) is None

    app = Quart(__name__)

    with pytest.raises(RuntimeError):
        async with app.test_request_context("/"):
            # app = app, silent = False
            # babel not in app.extensions
            get_state()

    # same as above, just silent
    async with app.test_request_context("/"):
        assert get_state(app=None, silent=True) == None

    Babel(app)

    async with app.test_request_context("/"):
        # should use current_app
        assert get_state(app=None, silent=True) == app.extensions['babel']


@pytest.mark.asyncio
async def test_get_locale():
    """
    Tests the `get_locale` function.
    """
    app = Quart(__name__)
    Babel(app)

    async with app.test_request_context("/"):
        assert get_locale() == Locale.parse("en")

@pytest.mark.asyncio
async def test_get_timezone_none():
    """
    Tests if `get_timezone` functions
    if timezone is None.
    """
    assert await get_timezone() is None

    app = Quart(__name__)
    babel = Babel(app)

    @babel.timezoneselector
    def tz_none():
        return None

    async with app.test_request_context("/"):
        assert await get_timezone() == UTC

@pytest.mark.asyncio
async def test_get_timezone_vienna():
    """
    Tests if the timezone is Vienna.
    """
    app = Quart(__name__)
    babel = Babel(app)

    @babel.timezoneselector
    def tz_vienna():
        return timezone('Europe/Vienna')

    async with app.test_request_context("/"):
        assert get_timezone() == timezone('Europe/Vienna')

@pytest.mark.asyncio
async def test_convert_timezone():
    """
    Tests converting the timezone.
    """
    app = Quart(__name__)
    Babel(app)

    date_time = datetime(2022, 8, 8, 17, 46)

    async with app.test_request_context("/"):
        dt_utc = to_utc(date_time)
        assert dt_utc.tzinfo is None

        dt_usertz = to_user_timezone(dt_utc)
        assert dt_usertz is not None
