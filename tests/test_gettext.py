"""
tests.test_gettext
"""
from typing import Any
import pytest

from babel import support
import quart

import quart_babel as babel
from quart_babel import gettext, lazy_gettext, lazy_ngettext, ngettext
from quart_babel.utils import get_babel


@pytest.mark.asyncio
async def test_basics() -> None:
    """
    Test basic gettext.
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE")

    async with app.test_request_context("/"):
        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 3) == "3 Äpfel"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "1 Apfel"


@pytest.mark.asyncio
async def test_template_basics() -> None:
    """
    Tests template basics
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE")

    async def t(x: Any) -> str:
        return await quart.render_template_string("{{ %s }}" % x)

    async with app.test_request_context("/"):
        assert await t("gettext('Hello %(name)s!', name='Peter')") == "Hallo Peter!"
        assert await t("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == "3 Äpfel"
        assert await t("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == "1 Apfel"

        value = await quart.render_template_string(
            """
            {% trans %}Hello {{ name }}!{% endtrans %}
        """,
            name="Peter",
        )

        assert value.strip() == "Hallo Peter!"

        value = await quart.render_template_string(
            """
            {% trans num=3 %}{{ num }} Apple
            {%- pluralize %}{{ num }} Apples{% endtrans %}
        """,
            name="Peter",
        )

        assert value.strip() == "3 Äpfel"


@pytest.mark.asyncio
async def test_lazy_gettext() -> None:
    """
    Test lazy_gettext
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE")
    yes = lazy_gettext("Yes")

    async with app.test_request_context("/"):
        assert str(yes) == "Ja"
        assert yes.__html__() == "Ja"

    get_babel(app).default_locale = "en_US"

    async with app.test_request_context("/"):
        assert str(yes) == "Yes"
        assert yes.__html__() == "Yes"


@pytest.mark.asyncio
async def test_lazy_ngettext() -> None:
    """
    Test lazy_ngettext
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE")
    one_apple = lazy_ngettext("%(num)s Apple", "%(num)s Apples", 1)

    async with app.test_request_context("/"):
        assert str(one_apple) == "1 Apfel"
        assert one_apple.__html__() == "1 Apfel"
    two_apples = lazy_ngettext("%(num)s Apple", "%(num)s Apples", 2)

    async with app.test_request_context("/"):
        assert str(two_apples) == "2 Äpfel"
        assert two_apples.__html__() == "2 Äpfel"


@pytest.mark.asyncio
async def test_lazy_gettext_defaultdomain() -> None:
    """
    Tests lazy_gettext for default domain
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE", default_domain="test")
    first = lazy_gettext("first")

    async with app.test_request_context("/"):
        assert str(first) == "erste"

    get_babel(app).default_locale = "en_US"

    async with app.test_request_context("/"):
        assert str(first) == "first"


@pytest.mark.asyncio
async def test_list_translations() -> None:
    """
    Tests list translations
    """
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale="de_DE")

    async with app.app_context():
        translations = b.list_translations()
        assert len(translations) == 3
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "ja"
        assert str(translations[2]) == "de_DE"


@pytest.mark.asyncio
async def test_list_translations_default_locale_exists() -> None:
    """
    Tests list translations for default locale exists
    """
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale="de")

    async with app.app_context():
        translations = b.list_translations()
        assert len(translations) == 2
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "ja"


@pytest.mark.asyncio
async def test_no_formatting() -> None:
    """
    Ensure we don't format strings unless a variable is passed.
    """
    app = quart.Quart(__name__)
    babel.Babel(app)

    async with app.test_request_context("/"):
        assert gettext("Test %s") == "Test %s"
        assert gettext("Test %(name)s", name="test") == "Test test"
        assert gettext("Test %s") % "test" == "Test test"


@pytest.mark.asyncio
async def test_domain() -> None:
    """
    Tests the domain
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE")
    domain = babel.Domain(domain="test")

    async with app.test_request_context("/"):
        assert domain.gettext("first") == "erste"
        assert babel.gettext("first") == "first"


@pytest.mark.asyncio
async def test_as_default() -> None:
    """
    Tests as default
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE")
    domain = babel.Domain(domain="test")

    async with app.test_request_context("/"):
        assert babel.gettext("first") == "first"
        domain.as_default()
        assert babel.gettext("first") == "erste"


@pytest.mark.asyncio
async def test_default_domain() -> None:
    """
    Tests default domain
    """
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale="de_DE", default_domain="test")

    async with app.test_request_context("/"):
        assert babel.gettext("first") == "erste"


@pytest.mark.asyncio
async def test_multiple_apps() -> None:
    """
    Tests multiple apps with gettext
    """
    app1 = quart.Quart(__name__)
    b1 = babel.Babel(app1, default_locale="de_DE")

    app2 = quart.Quart(__name__)
    b2 = babel.Babel(app2, default_locale="de_DE")

    async with app1.test_request_context("/"):
        assert babel.gettext("Yes") == "Ja"

        assert ("de_DE", "messages") in b1.domain_instance.get_translations_cache()

    async with app2.test_request_context("/"):
        assert "de_DE", "messages" not in b2.domain_instance.get_translations_cache()


@pytest.mark.asyncio
async def test_cache(mocker) -> None:
    """
    Tests cache
    """
    load_mock = mocker.patch(
        "babel.support.Translations.load", side_effect=support.Translations.load
    )

    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale="de_DE", locale_selector=lambda: the_locale)

    # first request, should load en_US
    the_locale = "en_US"
    async with app.test_request_context("/"):
        assert b.domain_instance.get_translations_cache() == {}
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 1

    # second request, should use en_US from cache
    async with app.test_request_context("/"):
        assert set(b.domain_instance.get_translations_cache()) == {
            ("en_US", "messages")
        }
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 1

    # third request, should load de_DE from cache
    the_locale = "de_DE"
    async with app.test_request_context("/"):
        assert set(b.domain_instance.get_translations_cache()) == {
            ("en_US", "messages")
        }
        assert babel.gettext("Yes") == "Ja"
    assert load_mock.call_count == 2

    # now everything is cached, so no more loads should happen!
    the_locale = "en_US"
    async with app.test_request_context("/"):
        assert set(b.domain_instance.get_translations_cache()) == {
            ("en_US", "messages"),
            ("de_DE", "messages"),
        }
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 2

    the_locale = "de_DE"
    async with app.test_request_context("/"):
        assert set(b.domain_instance.get_translations_cache()) == {
            ("en_US", "messages"),
            ("de_DE", "messages"),
        }
        assert babel.gettext("Yes") == "Ja"
    assert load_mock.call_count == 2


@pytest.mark.asyncio
async def test_plurals() -> None:
    """
    Tests plurals
    """
    app = quart.Quart(__name__)

    def set_locale() -> str:
        return quart.request.headers["LANG"]

    babel.Babel(app, locale_selector=set_locale)

    # Plural-Forms: nplurals=2; plural=(n != 1)
    async with app.test_request_context("/", headers={"LANG": "de_DE"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "1 Apfel"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "2 Äpfel"

    # Plural-Forms: nplurals=1; plural=0;
    async with app.test_request_context("/", headers={"LANG": "ja"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "リンゴ 1 個"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "リンゴ 2 個"


@pytest.mark.asyncio
async def test_plurals_different_domains() -> None:
    """
    Tests plurals on different domains
    """
    app = quart.Quart(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": [
                "translations",
                "translations_different_domain"
            ],
            "BABEL_DOMAIN": ["messages", "myapp"]
        }
    )

    def set_locale() -> str:
        return quart.request.headers["LANG"]

    babel.Babel(app, locale_selector=set_locale)

    # Plural-Forms: nplurals=2; plural=(n != 1)
    async with app.test_request_context("/", headers={"LANG": "de_DE"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "1 Apfel"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "2 Äpfel"

    # Plural-Forms: nplurals=1; plural=0;
    async with app.test_request_context("/", headers={"LANG": "ja"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "リンゴ 1 個"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "リンゴ 2 個"
