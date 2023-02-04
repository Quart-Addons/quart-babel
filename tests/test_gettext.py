"""
Test gettext functions including LazyStrings.
"""
from __future__ import annotations
import typing as t

import pytest
from quart import render_template_string

from quart_babel import (
    Domain,
    gettext,
    ngettext,
    pgettext,
    npgettext,
    lazy_gettext,
    lazy_pgettext,
    lazy_ngettext,
    switch_locale
)

from quart_babel.domain import get_domain

if t.TYPE_CHECKING:
    from quart import Quart
    from quart_babel import Babel

@pytest.mark.asyncio
async def test_basic_test(app: Quart, babel: Babel) -> None:
    """
    Test basic text translations.
    """
    babel(app, default_locale='de_DE')

    async with app.app_context():
        assert gettext('Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert ngettext('%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'
        assert ngettext('%(num)s Apple', '%(num)s Apples', 1) == '1 Apfel'
        assert pgettext('button', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert pgettext('dialog', 'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert pgettext('button', 'Hello Guest!') == 'Hallo Gast!'
        assert npgettext('shop', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'
        assert npgettext('fruits', '%(num)s Apple', '%(num)s Apples', 3) == '3 Äpfel'

@pytest.mark.asyncio
async def test_template_basics(app: Quart, babel: Babel) -> None:
    """
    Test template basics.
    """
    babel(app, default_locale='de_DE')

    async def trans(txt):
        return await render_template_string('{{ %s }}' % txt)

    async with app.app_context():
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
async def test_lazy_gettext(app: Quart, babel: Babel) -> None:
    """
    Test `lazy_gettext`.
    """
    babel(app, default_locale='de_DE')

    yes = lazy_gettext('Yes')

    async with app.app_context():
        assert str(yes) == 'Ja'

        with switch_locale('en_US'):
            assert str(yes) == 'Yes'

@pytest.mark.asyncio
async def test_no_formatting(app: Quart, babel: Babel) -> None:
    """
    Ensure we don't format a string unless a variable is passed.
    """
    babel(app)

    async with app.app_context():
        assert gettext('Test %s') == 'Test %s'
        assert gettext('Test %(name)s', name='test') == 'Test test'
        assert gettext('Test test') == 'Test test'

@pytest.mark.asyncio
async def test_lazy_gettext_default_domain(app: Quart, babel: Babel) -> None:
    """
    Tests `lazy_gettext` with the default domain.
    """
    domain = Domain(domain='test')
    babel(app, default_locale='de_DE', default_domain=domain)

    first = lazy_gettext('first')
    domain_first = domain.lazy_gettext('first')

    async with app.app_context():
        assert str(domain_first) == 'erste'
        assert str(first) == 'erste'

        with switch_locale('en-US'):
            assert str(first) == 'first'
            assert str(domain_first) == 'first'

@pytest.mark.asyncio
async def test_lazy_pgettext(app: Quart, babel: Babel) -> None:
    """
    Test `lazy_pgettext`
    """
    domain = Domain(domain='messages')
    babel(app, default_locale='de_DE', default_domain=domain)

    first = lazy_pgettext('button', 'Hello Guest!')
    domain_first = domain.lazy_pgettext('button', 'Hello Guest!')

    async with app.app_context():
        assert str(domain_first) == 'Hallo Gast!'
        assert str(first) == 'Hallo Gast!'

        with switch_locale('en-US'):
            assert str(first) == 'Hello Guest!'
            assert str(domain_first) == 'Hello Guest!'

@pytest.mark.asyncio
async def test_lazy_ngettext(app: Quart, babel: Babel) -> None:
    """
    Test `lazy_ngettext`
    """
    domain = Domain(domain='messages')
    babel(app, default_locale='de_DE', default_domain=domain)

    one_apple = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 1)
    one_apple_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 1)
    two_apples = lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)
    two_apples_d = domain.lazy_ngettext('%(num)s Apple', '%(num)s Apples', 2)

    async with app.app_context():
        assert str(one_apple) == '1 Apfel'
        assert str(one_apple_d) == '1 Apfel'
        assert str(two_apples) == '2 Äpfel'
        assert str(two_apples_d) == '2 Äpfel'

def test_no_ctx_gettext(app: Quart, babel: Babel) -> None:
    """
    Tests the extension with no app context.
    """
    babel(app, default_locale='de_DE')
    domain = get_domain()
    assert domain.gettext('Yes') == 'Yes'
