"""
Tests getttext.
"""
import aiounittest
from babel import support
from quart import Quart, render_template_string
import quart_babel as babel_ext
from quart_babel import gettext, ngettext, pgettext, npgettext, \
    lazy_gettext, lazy_pgettext, lazy_ngettext

class GettextTestCase(aiounittest.AsyncTestCase):

    async def test_basics(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')

        async with app.test_request_context("/"):
            assert gettext('Hello %(name)s!', name='Peter') == 'Hallo Peter!'
            assert ngettext('%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'  # noqa
            assert ngettext('%(num)s Apple', '%(num)s Apples', 1) == '1 Apfel'  # noqa

            assert pgettext('button', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'  # noqa
            assert pgettext('dialog', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'  # noqa
            assert pgettext('button', 'Hello Guest!') == 'Hallo Gast!'
            assert npgettext('shop', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'  # noqa
            assert npgettext('fruits', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'  # noqa

    async def test_template_basics(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')

        async def t(x):
            return await render_template_string('{{ %s }}' % x)

        async with app.test_request_context("/"):
            assert await t("gettext('Hello %(name)s!', name='Peter')") == 'Hallo Peter!'  # noqa
            assert await t("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == '3 Äpfel'  # noqa
            assert await t("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == '1 Apfel'  # noqa
            assert await render_template_string('''
                {% trans %}Hello {{ name }}!{% endtrans %}
            ''', name='Peter').strip() == 'Hallo Peter!'
            assert await render_template_string('''
                {% trans num=3 %}{{ num }} Apple
                {%- pluralize %}{{ num }} Apples{% endtrans %}
            ''', name='Peter').strip() == '3 Äpfel'

    async def test_lazy_gettext(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')
        yes = lazy_gettext('Yes')
        async with app.test_request_context("/"):
            assert str(yes) == 'Ja'
        app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
        async with app.test_request_context("/"):
            assert str(yes) == 'Yes'

    async def test_no_formatting(self):
        """
        Ensure we don't format strings unless a variable is passed.
        """
        app = Quart(__name__)
        babel_ext.Babel(app)

        async with app.test_request_context("/"):
            assert gettext('Test %s') == 'Test %s'
            assert gettext('Test %(name)s', name='test') == 'Test test'
            assert gettext('Test %s') % 'test' == 'Test test'

    async def test_lazy_gettext_defaultdomain(self):
        app = Quart(__name__)
        domain = babel_ext.Domain(domain='test')
        babel_ext.Babel(app, default_locale='de_DE', default_domain=domain)
        first = lazy_gettext('first')
        domain_first = domain.lazy_gettext('first')

        async with app.test_request_context("/"):
            assert str(domain_first) == 'erste'
            assert str(first) == 'erste'

        app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
        async with app.test_request_context("/"):
            assert str(first) == 'first'
            assert str(domain_first) == 'first'

    async def test_lazy_pgettext(self):
        app = Quart(__name__)
        domain = babel_ext.Domain(domain='messages')
        babel_ext.Babel(app, default_locale='de_DE')
        first = lazy_pgettext('button', 'Hello Guest!')
        domain_first = domain.lazy_pgettext('button', 'Hello Guest!')

        async with app.test_request_context("/"):
            assert str(domain_first) == 'Hallo Gast!'
            assert str(first) == 'Hallo Gast!'

        app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
        async with app.test_request_context("/"):
            assert str(first) == 'Hello Guest!'
            assert str(domain_first) == 'Hello Guest!'

    async def test_lazy_ngettext(self):
        app = Quart(__name__)
        domain = babel_ext.Domain(domain='messages')
        babel_ext.Babel(app, default_locale='de_DE')

        one_apple = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 1)
        one_apple_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 1)  # noqa
        async with app.test_request_context("/"):
            assert str(one_apple) == '1 Apfel'
            assert str(one_apple_d) == '1 Apfel'

        two_apples = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)
        two_apples_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)  # noqa
        async with app.test_request_context("/"):
            assert str(two_apples) == '2 Äpfel'
            assert str(two_apples_d) == '2 Äpfel'

    async def test_no_ctx_gettext(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')
        domain = babel_ext.get_domain()
        assert domain.gettext('Yes') == 'Yes'

    async def test_list_translations(self):
        app = Quart(__name__)
        b = babel_ext.Babel(app, default_locale='de_DE')

        # an app_context is automatically created when a request context
        # is pushed if necessary
        async with app.test_request_context("/"):
            translations = b.list_translations()
            assert len(translations) == 1
            assert str(translations[0]) == 'de'

    async def test_get_translations(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')
        domain = babel_ext.get_domain()  # using default domain

        # no app context
        assert isinstance(domain.get_translations(), support.NullTranslations)

    async def test_domain(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')
        domain = babel_ext.Domain(domain='test')

        async with app.test_request_context("/"):
            assert domain.gettext('first') == 'erste'
            assert babel_ext.gettext('first') == 'first'

    async def test_as_default(self):
        app = Quart(__name__)
        babel_ext.Babel(app, default_locale='de_DE')
        domain = babel_ext.Domain(domain='test')

        async with app.test_request_context("/"):
            assert babel_ext.gettext('first') == 'first'
            domain.as_default()
            assert babel_ext.gettext('first') == 'erste'

    async def test_default_domain(self):
        app = Quart(__name__)
        domain = babel_ext.Domain(domain='test')
        babel_ext.Babel(app, default_locale='de_DE', default_domain=domain)

        async with app.test_request_context("/"):
            assert babel_ext.gettext('first') == 'erste'

    async def test_multiple_apps(self):
        app1 = Quart(__name__)
        babel_ext.Babel(app1, default_locale='de_DE')

        app2 = Quart(__name__)
        babel_ext.Babel(app2, default_locale='de_DE')

        async with app1.test_request_context("/"):
            assert babel_ext.gettext('Yes') == 'Ja'
            assert 'de_DE' in app1.extensions["babel"].domain.cache

        async with app2.test_request_context("/"):
            assert 'de_DE' not in app2.extensions["babel"].domain.cache
