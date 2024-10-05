"""
tests.test_multiple_apps
"""
import pytest

import quart
import quart_babel as babel


@pytest.mark.asyncio
async def test_multiple_app() -> None:
    """
    Test multiple apps.
    """
    b = babel.Babel()

    app1 = quart.Quart(__name__)
    b.init_app(app1, default_locale="de_DE")

    app2 = quart.Quart(__name__)
    b.init_app(app2, default_locale="en_us")

    async with app1.test_request_context("/"):
        assert str(babel.get_locale()) == "de_DE"
        assert babel.gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"

    async with app2.test_request_context("/"):
        assert str(babel.get_locale()) == "en_US"
        assert babel.gettext("Hello %(name)s!", name="Peter") == "Hello Peter!"
