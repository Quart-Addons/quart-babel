"""
Test Quart-Babel Integration.
"""
from datetime import datetime

import pytest
from babel import support
from quart import Quart

from quart_babel import (
    Babel,
    gettext,
    switch_locale,
    refresh_locale,
    switch_timezone,
    refresh_timezone
    )

from quart_babel import to_user_timezone, to_utc
from quart_babel.domain import get_domain
from quart_babel.locale import get_locale, set_locale
from quart_babel.timezone import get_timezone, set_timezone
from quart_babel.typing import ASGIRequest
from quart_babel.utils import get_state

def test_configure_jinja(app: Quart, babel: Babel) -> None:
    """
    Test jinja configuration for Babel.
    """
    babel(app, configure_jinja=False)
    assert not app.jinja_env.filters.get("scientificformat")

@pytest.mark.asyncio
async def test_get_state(app: Quart, babel: Babel) -> None:
    """
    Test the `get_state` function.
    """
    # app = None, app.extensions = False, babel = False, silent = True
    assert get_state(silent=True) is None

    with pytest.raises(RuntimeError):
        async with app.app_context():
            # app = app, silent = False
            # babel not in app.extensions
            get_state()

    # same as above, but just silent.
    async with app.app_context():
        assert get_state(app=None, silent=True) is None

    babel(app)

    async with app.test_request_context("/"):
        # should use current_app
        assert get_state(app=None, silent=True) == app.extensions['babel']

def test_switch_locale(app: Quart, babel: Babel) -> None:
    """
    Test switch locale generator.
    """
    babel(app)

    set_locale('en-US')
    with switch_locale('be-BY'):
        assert str(get_locale()) == 'be_BY'
    assert str(get_locale()) == 'en_US'

def test_switch_timezone(app: Quart, babel: Babel) -> None:
    """
    Test switch timezone generator.
    """
    babel(app)

    set_timezone('America/New_York')
    with switch_timezone('Europe/Vienna'):
        assert str(get_timezone()) == 'Europe/Vienna'
    assert str(get_timezone()) == 'America/New_York'

def test_refresh_locale(app: Quart, babel: Babel) -> None:
    """
    Test refresh locale function.
    """
    babel(app)

    set_locale('en-US')
    refresh_locale('be-BY')
    assert str(get_locale()) == 'be_BY'

def test_refresh_timezone(app: Quart, babel: Babel) -> None:
    """
    Test refresh timezone function.
    """
    babel(app)

    set_timezone('America/New_York')
    refresh_timezone('Europe/Vienna')
    assert str(get_timezone()) == 'Europe/Vienna'

@pytest.mark.asyncio
async def test_init_app(app: Quart, babel: Babel) -> None:
    """
    Test init_app method of Quart Babel.
    """
    async def timezone(request: ASGIRequest) -> str:
        return 'UTC'

    babel = babel()
    babel.init_app(app, timezone_selector=timezone)

    client = app.test_client()

    res = await client.get('/datetime')
    assert await res.get_data(as_text=True) == 'Apr 12, 2010, 1:46:00\u202fPM'

    res = await client.get('/date')
    assert await res.get_data(as_text=True) == 'Apr 12, 2010'

    res = await client.get('/time')
    assert await res.get_data(as_text=True) == '1:46:00\u202fPM'

    res = await client.get('/timedelta')
    assert await res.get_data(as_text=True) == '6 days'

def test_convert_timezone(app: Quart, babel: Babel) -> None:
    """
    Test converting a timezone.
    """
    babel(app)

    dtime = datetime(2022, 8, 8, 17, 46)

    dt_utc = to_utc(dtime)
    assert dt_utc.tzinfo is None

    dt_usertz = to_user_timezone(dt_utc)
    assert dt_usertz is not None

@pytest.mark.asyncio
async def test_list_translations(app: Quart, babel: Babel) -> None:
    """
    Test listing translations.
    """
    babel = babel(app, default_locale="de_DE")

    async with app.app_context():
        translations = babel.list_translations()
        assert len(translations) == 2
        assert str(translations[0]) == 'de'

@pytest.mark.asyncio
async def test_get_translations(app: Quart, babel: Babel) -> Babel:
    """
    Test getting translations.
    """
    babel(app, default_locale="de_DE")
    domain = get_domain() # using default domain

    # No app context
    assert isinstance(domain.translations, support.NullTranslations)

@pytest.mark.asyncio
async def test_multiple_apps() -> None:
    """
    Test multiple applications.
    """
    app1 = Quart(__name__)
    Babel(app1, default_locale='de_DE')

    app2 = Quart(__name__)
    Babel(app2, default_locale='de_DE')

    async with app1.app_context():
        assert gettext('Yes') == 'Ja'
        assert 'de_DE' in app1.extensions["babel"].domain.cache

    async with app2.app_context():
        assert 'de_DE' not in app2.extensions["babel"].domain.cache
