"""
tests.test_integration
"""
import pickle

import pytest

from babel.support import NullTranslations
import quart
import quart_babel as babel
from quart_babel import gettext, lazy_gettext
from quart_babel.domain import get_translations


@pytest.mark.asyncio
async def test_no_request_context() -> None:
    """
    Tests no request context
    """
    b = babel.Babel()
    app = quart.Quart(__name__)
    b.init_app(app)

    async with app.app_context():
        assert isinstance(get_translations(), NullTranslations)


@pytest.mark.asyncio
async def test_multiple_directories() -> None:
    """
    Ensure we can load translations from multiple directories.

    This also ensures that directories without any translation files
    are not taken into account.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": [
                "translations",
                "renamed_translations"
            ],
            "BABEL_DEFAULT_LOCALE": "de_DE"
        }
    )

    b.init_app(app)

    async with app.test_request_context("/"):
        translations = b.list_translations()

        assert len(translations) == 4
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "ja"
        assert str(translations[2]) == "de"
        assert str(translations[3]) == "de_DE"

        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"


@pytest.mark.asyncio
async def test_multiple_directories_multiple_domains() -> None:
    """
    Ensure we can load translations from multiple directories with a
    custom domain.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": [
                "renamed_translations",
                "translations_different_domain"
            ],
            "BABEL_DEFAULT_LOCALE": "de_DE",
            "BABEL_DOMAIN": ["messages", "myapp"]
        }
    )

    b.init_app(app)

    async with app.test_request_context("/"):
        translations = b.list_translations()

        assert len(translations) == 3
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de"
        assert str(translations[2]) == "de_DE"

        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
        assert gettext("Good bye") == "Auf Wiedersehen"


@pytest.mark.asyncio
async def test_multiple_directories_different_domain() -> None:
    """
    Ensure we can load translations from multiple directories with a
    custom domain.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": [
                "translations_different_domain",
                "renamed_translations"
            ],
            "BABEL_DEFAULT_LOCALE": "de_DE",
            "BABEL_DOMAIN": "myapp"
        }
    )

    b.init_app(app)

    async with app.test_request_context("/"):
        translations = b.list_translations()

        assert len(translations) == 3
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de"
        assert str(translations[2]) == "de_DE"

        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
        assert gettext("Good bye") == "Auf Wiedersehen"


@pytest.mark.asyncio
async def test_different_domain() -> None:
    """
    Ensure we can load translations from multiple directories.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": "translations_different_domain",
            "BABEL_DEFAULT_LOCALE": "de_DE",
            "BABEL_DOMAIN": "myapp",
        }
    )

    b.init_app(app)

    async with app.test_request_context("/"):
        translations = b.list_translations()

        assert len(translations) == 2
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de_DE"

        assert gettext("Good bye") == "Auf Wiedersehen"


def test_lazy_old_style_formatting() -> None:
    """
    Tests old style of lazy formatting.
    """
    lazy_string = lazy_gettext("Hello %(name)s")
    assert lazy_string % {"name": "test"} == "Hello test"

    lazy_string = lazy_gettext("test")
    assert f"Hello {lazy_string}" == "Hello test"


def test_lazy_pickling() -> None:
    """
    Test lazy pickling
    """
    lazy_string = lazy_gettext("Foo")
    pickled = pickle.dumps(lazy_string)
    unpickled = pickle.loads(pickled)

    assert unpickled == lazy_string
