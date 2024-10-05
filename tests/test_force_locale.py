"""
tests.test_force_locale
"""
import asyncio
import pytest

import quart
import quart_babel as babel


@pytest.mark.asyncio
async def test_force_locale() -> None:
    """
    Tests force_locale
    """
    app = quart.Quart(__name__)
    babel.Babel(app, locale_selector=lambda: "de_DE")

    async with app.test_request_context("/"):
        assert str(babel.get_locale()) == "de_DE"
        with babel.force_locale("en_US"):
            assert str(babel.get_locale()) == "en_US"
        assert str(babel.get_locale()) == "de_DE"


@pytest.mark.asyncio
async def test_force_locale_multiple() -> None:
    """
    Test multiples with force locale.
    """
    app = quart.Quart(__name__)
    babel.Babel(app, locale_selector=lambda: "de_DE")

    async def first_request() -> None:
        async with app.test_request_context("/"):
            with babel.force_locale("en_US"):
                assert str(babel.get_locale()) == "en_US"
        await asyncio.sleep(0.5)

    async def second_request() -> None:
        async with app.test_request_context("/"):
            assert str(babel.get_locale()) == "de_DE"
        await asyncio.sleep(0.8)

    tasks = []
    tasks.append(asyncio.create_task(first_request()))
    tasks.append(asyncio.create_task(second_request()))

    await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test_force_locale_multiple_and_app_context() -> None:
    """
    Test multiples with force locale with app context.
    """
    app = quart.Quart(__name__)
    babel.Babel(app, locale_selector=lambda: "de_DE")

    async def first_request() -> None:
        async with app.app_context():
            with babel.force_locale("en_US"):
                assert str(babel.get_locale()) == "en_US"
        await asyncio.sleep(0.5)

    async def second_request() -> None:
        async with app.app_context():
            assert str(babel.get_locale()) == "de_DE"
        await asyncio.sleep(0.8)

    tasks = []
    tasks.append(asyncio.create_task(first_request()))
    tasks.append(asyncio.create_task(second_request()))

    await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test_refresh_during_force_locale() -> None:
    """
    Tests refresh during force locale
    """
    app = quart.Quart(__name__)
    babel.Babel(app, locale_selector=lambda: "de_DE")

    async with app.test_request_context("/"):
        with babel.force_locale("en_US"):
            assert str(babel.get_locale()) == "en_US"
            babel.refresh()
            assert str(babel.get_locale()) == "en_US"
