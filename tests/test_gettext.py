"""
Test gettext with Quart Babel.
"""
import pytest
from babel import support

from quart import Quart, render_template_string
from quart_babel import (Babel, Domain, gettext, ngettext, pgettext,
                        npgettext, lazy_gettext, lazy_pgettext,
                        lazy_ngettext, get_domain)

@pytest.mark.asyncio
async def test_basic_text():
    """
    Tests basic text translations.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')

    async with app.test_request_context("/"):
        assert gettext('Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert ngettext('%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'
        assert ngettext('%(num)s Apple', '%(num)s Apples', 1) == '1 Apfel'
        assert pgettext('button', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert pgettext('dialog', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert pgettext('button', 'Hello Guest!') == 'Hallo Gast!'
        assert npgettext('shop', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'
        assert npgettext('fruits', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'

@pytest.mark.asyncio
async def test_template_basics():
    """
    Tests templates text translations.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')

    async def trans(txt):
        return await render_template_string('{{ %s }}' % txt)

    async with app.test_request_context("/"):
        assert await trans("gettext('Hello %(name)s!', name='Peter')") == 'Hallo Peter!'  
        assert await trans("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == u'3 Äpfel'
        assert await trans("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == u'1 Apfel'
        assert await render_template_string('''
            {% trans %}Hello {{ name }}!{% endtrans %}
        ''', name='Peter').strip() == 'Hallo Peter!'
        assert await render_template_string('''
            {% trans num=3 %}{{ num }} Apple
            {%- pluralize %}{{ num }} Apples{% endtrans %}
        ''', name='Peter').strip() == u'3 Äpfel'
    
@pytest.mark.asyncio
async def test_lazy_gettext():
    """
    Tests `lazy_gettext`.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')

    yes = lazy_gettext('Yes')

    async with app.test_request_context("/"):
        assert str(yes) == 'Ja'
    
    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'

    async with app.test_request_context("/"):
        assert str(yes) == 'Yes'

@pytest.mark.asyncio
async def test_no_formatting():
    """
    Ensure we don't format string unless a
    variable is passed.
    """
    app = Quart(__name__)
    Babel(app)

    async with app.test_request_context("/"):
        assert gettext('Test %s') == 'Test %s'
        assert gettext('Test %(name)s', name='test') == 'Test test'
        assert gettext('Test %s') % 'test' == 'Test test'

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
        assert str(domain_first) == 'erste'
        assert str(first) == 'erste'

    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'

    async with app.test_request_context("/"):
        assert str(first) == 'first'
        assert str(domain_first) == 'first'

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
        assert str(domain_first) == 'Hallo Gast!'
        assert str(first) == 'Hallo Gast!'
    
    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'

    async with app.test_request_context("/"):
        assert str(first) == 'Hello Guest!'
        assert str(domain_first) == 'Hello Guest!'

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
        assert str(one_apple) == '1 Apfel'
        assert str(one_apple_d) == '1 Apfel'

    two_apples = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)
    two_apples_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)

    async with app.test_request_context("/"):
        assert str(two_apples) == '2 Äpfel'
        assert str(two_apples_d) == '2 Äpfel'

def test_no_ctx_gettext():
    """
    Tests the extension with no app context.
    """
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    domain = get_domain()
    assert domain.gettext('Yes') == 'Yes'

@pytest.mark.asyncio
async def test_list_translations():
    app = Quart(__name__)
    babel = Babel(app, default_locale='de_DE')

    # an app_context is automatically created when a request context
    # is pushed if necessary
    async with app.test_request_context("/"):
        translations = babel.list_translations()
        assert len(translations) == 1
        assert str(translations[0]) == 'de'

def test_get_translations():
    app = Quart(__name__)
    Babel(app, default_locale='de_DE')
    domain = get_domain()  # using default domain

    # no app context
    assert isinstance(domain.get_translations(), support.NullTranslations)