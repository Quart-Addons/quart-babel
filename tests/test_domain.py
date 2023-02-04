"""
Tests the Domain(s).
"""
from __future__ import annotations
import typing as t

import pytest

from quart_babel import Domain, gettext

if t.TYPE_CHECKING:
    from quart import Quart
    from quart_babel import Babel

@pytest.mark.asyncio
async def test_domain(app: Quart, babel: Babel) -> None:
    """
    Test domain.
    """
    babel(app, default_locale="de_DE")
    domain = Domain(domain='test')

    async with app.app_context():
        assert domain.gettext('first') == 'erste'
        assert gettext('first') == 'first'

@pytest.mark.asyncio
async def test_as_default(app: Quart, babel: Babel) -> None:
    """
    Test domain as default.
    """
    babel(app, default_locale="de_DE")
    domain = Domain(domain='test')

    async with app.app_context():
        assert gettext('first') == 'first'
        domain.as_default
        assert gettext('first') == 'erste'

@pytest.mark.asyncio
async def test_default_domain(app: Quart, babel: Babel) -> None:
    """
    Test default domain.
    """
    domain = Domain(domain='test')
    babel(app, default_locale="de_DE", default_domain=domain)

    async with app.app_context():
        assert gettext('first') == 'erste'
