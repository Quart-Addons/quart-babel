"""
Tests date formatting.
"""
import asyncio
from datetime import datetime, timedelta
import aiounittest

from quart import Quart
import quart_babel as babel_ext
from quart_babel.utils.formats import _get_format

class DateFormattingTestCase(aiounittest.AsyncTestCase):

    async def test_basics(self):
        app = Quart(__name__)
        babel_ext.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)
        delta = timedelta(days=6)

        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
            assert babel_ext.format_date(d) == 'Apr 12, 2010'
            assert babel_ext.format_time(d) == '1:46:00 PM'
            assert babel_ext.format_timedelta(delta) == '1 week'
            assert babel_ext.format_timedelta(delta, threshold=1) == '6 days'

        async with app.test_request_context("/"):
            app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
            assert babel_ext.format_date(d) == 'Apr 12, 2010'
            assert babel_ext.format_time(d) == '3:46:00 PM'

        async with app.test_request_context("/"):
            app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE'
            assert babel_ext.format_datetime(d, 'long') == \
                '12. April 2010 um 15:46:00 MESZ'
    
    async def test_init_app(self):
        b = babel_ext.Babel()
        app = Quart(__name__)
        b.init_app(app)
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

    async def test_custom_formats(self):
        app = Quart(__name__)
        app.config.update(
            BABEL_DEFAULT_LOCALE='en_US',
            BABEL_DEFAULT_TIMEZONE='Pacific/Johnston'
        )
        b = babel_ext.Babel(app)
        b.date_formats['datetime'] = 'long'
        b.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'

        b.date_formats['date'] = 'long'
        b.date_formats['date.short'] = 'MM d'

        d = datetime(2010, 4, 12, 13, 46)

        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == 'April 12, 2010 3:46:00 AM'
            assert _get_format('datetime') == 'MMMM d, yyyy h:mm:ss a'
            # none; returns the format
            assert _get_format('datetime', 'medium') == 'medium'
            assert _get_format('date', 'short') == 'MM d'

    async def test_custom_locale_selector(self):
        app = Quart(__name__)
        b = babel_ext.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)

        the_timezone = 'UTC'
        the_locale = 'en_US'

        @b.localeselector
        def select_locale():
            return the_locale

        @b.timezoneselector
        def select_timezone():
            return the_timezone

        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'

        the_locale = 'de_DE'
        the_timezone = 'Europe/Vienna'

        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == '12.04.2010, 15:46:00'

    async def test_custom_async_locale_selector(self):
        app = Quart(__name__)
        b = babel_ext.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)

        the_timezone = 'UTC'
        the_locale = 'en_US'

        @b.localeselector
        async def select_locale():
            await asyncio.sleep(0.1)
            return the_locale

        @b.timezoneselector
        async def select_timezone():
            await asyncio.sleep(0.2)
            return the_timezone

        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'

        the_locale = 'de_DE'
        the_timezone = 'Europe/Vienna'

        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == '12.04.2010, 15:46:00'

    async def test_refreshing(self):
        app = Quart(__name__)
        babel_ext.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)
        babel_ext.refresh()  # nothing should be refreshed (see case below)
        async with app.test_request_context("/"):
            assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
            app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            babel_ext.refresh()
            assert babel_ext.format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'

    async def test_force_locale(self):
        app = Quart(__name__)
        b = babel_ext.Babel(app)

        @b.localeselector
        def select_locale():
            return 'de_DE'

        with babel_ext.force_locale('en_US'):
            assert babel_ext.get_locale() is None

        async with app.test_request_context("/"):
            assert str(babel_ext.get_locale()) == 'de_DE'
            with babel_ext.force_locale('en_US'):
                assert str(babel_ext.get_locale()) == 'en_US'
            assert str(babel_ext.get_locale()) == 'de_DE'
