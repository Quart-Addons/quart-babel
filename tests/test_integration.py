"""
Test babel integration.
"""
from datetime import datetime
import pytest
from babel import Locale
from pytz import timezone, UTC

from quart import Quart
import quart_babel as babel_ext
from quart_babel.utils.context import get_state

@pytest.mark.asyncio
class IntegrationTestCase():
    def test_configure_jinja(self):
        app = Quart(__name__)
        babel_ext.Babel(app, configure_jinja=False)
        assert not app.jinja_env.filters.get("scientificformat")

    async def test_get_state(self):
        # app = None; app.extensions = False; babel = False; silent = True;
        assert get_state(silent=True) is None

        app = Quart(__name__)
        with pytest.raises(RuntimeError):
            async with app.test_request_context("/"):
                # app = app; silent = False
                # babel not in app.extensions
                get_state()

        # same as above, just silent
        async with app.test_request_context("/"):
            assert get_state(app=app, silent=True) is None

        babel_ext.Babel(app)
        async with app.test_request_context("/"):
            # should use current_app
            assert get_state(app=None, silent=True) == app.extensions['babel']

    async def test_get_locale(self):
        assert babel_ext.get_locale() is None

        app = Quart(__name__)
        babel_ext.Babel(app)
        async with app.app_context():
            assert babel_ext.get_locale() == Locale.parse("en")

    async def test_get_timezone_none(self):
        assert babel_ext.get_timezone() is None

        app = Quart(__name__)
        b = babel_ext.Babel(app)

        @b.timezoneselector
        def tz_none():
            return None
        async with app.test_request_context("/"):
            assert babel_ext.get_timezone() == UTC

    async def test_get_timezone_vienna(self):
        app = Quart(__name__)
        b = babel_ext.Babel(app)

        @b.timezoneselector
        def tz_vienna():
            return timezone('Europe/Vienna')
        async with app.test_request_context("/"):
            assert babel_ext.get_timezone() == timezone('Europe/Vienna')

    async def test_convert_timezone(self):
        app = Quart(__name__)
        babel_ext.Babel(app)
        dt = datetime(2010, 4, 12, 13, 46)

        async with app.test_request_context("/"):
            dt_utc = babel_ext.to_utc(dt)
            assert dt_utc.tzinfo is None

            dt_usertz = babel_ext.to_user_timezone(dt_utc)
            assert dt_usertz is not None
