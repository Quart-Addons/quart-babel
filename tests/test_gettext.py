"""
Test gettext with Quart Babel.
"""
import asyncio
import pytest
from babel import support

from quart import Quart, render_template_string
from quart_babel import (Babel, Domain, gettext, ngettext, pgettext,
                        npgettext, lazy_gettext, lazy_pgettext,
                        lazy_ngettext, get_domain)

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_basic_text():
    """
    Tests basic text translations.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')

    async with app.test_request_context("/"):
        assert await gettext('Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert await ngettext('%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'
        assert await ngettext('%(num)s Apple', '%(num)s Apples', 1) == '1 Apfel'
        assert await pgettext('button', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert await pgettext('dialog', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert await pgettext('button', 'Hello Guest!') == 'Hallo Gast!'
        assert await npgettext('shop', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'
        assert await npgettext('fruits', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'

@pytest.mark.asyncio
async def test_template_basics():
    """
    Tests templates text translations.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    await app.startup()

    async def trans(txt):
        return await render_template_string('{{ %s }}' % txt)

    async with app.test_request_context("/"):
        assert await trans("gettext('Hello %(name)s!', name='Peter')") == 'Hallo Peter!'
        assert await trans("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == '3 Äpfel'
        assert await trans("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == '1 Apfel'
        assert (await render_template_string('''
            {% trans %}Hello {{ name }}!{% endtrans %}
        ''', name='Peter')).strip() == 'Hallo Peter!'
        assert (await render_template_string('''
            {% trans num=3 %}{{ num }} Apple
            {%- pluralize %}{{ num }} Apples{% endtrans %}
        ''', name='Peter')).strip() == '3 Äpfel'

@pytest.mark.asyncio
async def test_lazy_gettext():
    """
    Tests `lazy_gettext`.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')

    yes = lazy_gettext('Yes')

    async with app.test_request_context("/"):
        assert str(await yes) == 'Ja'

    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'

    async with app.test_request_context("/"):
        assert str(await yes) == 'Yes'

@pytest.mark.asyncio
async def test_no_formatting():
    """
    Ensure we don't format string unless a
    variable is passed.
    """
    app = Quart(__name__)
    Babel(app)

    async with app.test_request_context("/"):
        assert await gettext('Test %s') == 'Test %s'
        assert await gettext('Test %(name)s', name='test') == 'Test test'
        assert await gettext('Test test') == 'Test test'

@pytest.mark.asyncio
async def test_lazy_gettext_defaultdomain():
    """
    Tests `lazy_gettext` with the default domain.
    """
    app = Quart(__name__)
    domain = Domain(domain='test')
    Babel(app, default_locale='de_DE', default_domain=domain)

    first = lazy_gettext('first')
    domain_first = domain.lazy_gettext('first')

    async with app.test_request_context("/"):
        assert str(await domain_first) == 'erste'
        assert str(await first) == 'erste'

    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'

    async with app.test_request_context("/"):
        assert str(await first) == 'first'
        assert str(await domain_first) == 'first'

@pytest.mark.asyncio
async def test_lazy_pgettext():
    """
    Tests `lazy_pgettext`
    """
    app = Quart(__name__)
    domain = Domain(domain='messages')
    Babel(app, default_locale='de_DE')

    first = lazy_pgettext('button', 'Hello Guest!')
    domain_first = domain.lazy_pgettext('button', 'Hello Guest!')

    async with app.test_request_context("/"):
        assert str(await domain_first) == 'Hallo Gast!'
        assert str(await first) == 'Hallo Gast!'

    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'

    async with app.test_request_context("/"):
        assert str(await first) == 'Hello Guest!'
        assert str(await domain_first) == 'Hello Guest!'

@pytest.mark.asyncio
async def test_lazy_ngettext():
    """
    Tests `lazy_ngettext`
    """
    app = Quart(__name__)
    domain = Domain(domain='messages')
    Babel(app, default_locale='de_DE')

    one_apple = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 1)
    one_apple_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 1)

    async with app.test_request_context("/"):
        assert str(await one_apple) == '1 Apfel'
        assert str(await one_apple_d) == '1 Apfel'

    two_apples = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)
    two_apples_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)

    async with app.test_request_context("/"):
        assert str(await two_apples) == '2 Äpfel'
        assert str(await two_apples_d) == '2 Äpfel'

@pytest.mark.asyncio
async def test_no_ctx_gettext():
    """
    Tests the extension with no app context.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    domain = get_domain()
    assert await domain.gettext('Yes') == 'Yes'

@pytest.mark.asyncio
async def test_list_translations():
    """
    Tests listing translations.
    """
    app = Quart(__name__)
    babel = Babel(app, default_locale='de_DE')

    # an app_context is automatically created when a request context
    # is pushed if necessary
    async with app.test_request_context("/"):
        translations = babel.list_translations()
        assert len(translations) == 1
        assert str(translations[0]) == 'de'

@pytest.mark.asyncio
async def test_get_translations():
    """
    Tests getting tranlations.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    domain = get_domain()  # using default domain

    # no app context
    assert isinstance(await domain.get_translations(), support.NullTranslations)

@pytest.mark.asyncio
async def test_domain():
    """
    Test domain.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    domain = Domain(domain='test')

    async with app.test_request_context("/"):
        assert await domain.gettext('first') == 'erste'
        assert await gettext('first') == 'first'

@pytest.mark.asyncio
async def test_as_default():
    """
    Test domain as default.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    domain = Domain(domain='test')

    async with app.test_request_context("/"):
        assert await gettext('first') == 'first'
        domain.as_default()
        assert await gettext('first') == 'erste'

@pytest.mark.asyncio
async def test_default_domain():
    """
    Test default domain.
    """
    app = Quart(__name__)
    domain = Domain(domain='test')
    Babel(app, default_locale='de_DE', default_domain=domain)

    async with app.test_request_context("/"):
        assert await gettext('first') == 'erste'

@pytest.mark.asyncio
async def test_multiple_apps():
    """
    Test multiple applications.
    """
    app1 = Quart(__name__)
    Babel(app1, default_locale='de_DE')

    app2 = Quart(__name__)
    Babel(app2, default_locale='de_DE')

    async with app1.test_request_context("/"):
        assert await gettext('Yes') == 'Ja'
        assert 'de_DE' in app1.extensions["babel"].domain.cache

    async with app2.test_request_context("/"):
        assert 'de_DE' not in app2.extensions["babel"].domain.cache
