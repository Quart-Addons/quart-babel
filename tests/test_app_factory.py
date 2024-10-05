"""
tests.test_app_factory
"""
import pytest
import quart
import quart_babel as babel


@pytest.mark.asyncio
async def test_app_factory() -> None:
    """
    Tests the app factory.
    """
    b = babel.Babel()

    def locale_selector() -> str:
        return "de_DE"

    def create_app() -> quart.Quart:
        app_ = quart.Quart(__name__)
        b.init_app(app_, default_locale="en_US", locale_selector=locale_selector)
        return app_

    app = create_app()

    async with app.test_request_context("/"):
        assert str(babel.get_locale()) == "de_DE"
        assert babel.gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
