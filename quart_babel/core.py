"""
quart_babel.core
"""
from __future__ import annotations
import os
import typing as t

from .const import (
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
    DEFAULT_DATE_FORMATS
    )

from .domain import Domain, get_domain

from .formatters import (
    format_datetime,
    format_date,
    format_time,
    format_timedelta,
    format_number,
    format_decimal,
    format_currency,
    format_percent,
    format_scientific
)

from .locale import get_locale
from .middleware import QuartBabelMiddleware
from .timezone import get_timezone

from .typing import (
    LocaleSelectorFunc,
    TimezoneSelectorFunc,
    Translations
)

from .utils import (
    BabelState,
    get_state,
    convert_locale,
    convert_timezone
    )

if t.TYPE_CHECKING:
    from pytz import BaseTzInfo
    from babel import Locale
    from quart import Quart


class Babel(object):
    """
    The core class of Quart Babel. It is used to configure
    how babel is used with your `quart.Quart` application.

    Attributes:
        locale_selector: Custom locale selector function. Defaults
            to ``None``.
        timezone_selector: Custom timezone selector function. Defaults
            to ``None``.
    """
    locale_selector: LocaleSelectorFunc | None = None
    timezone_selector: TimezoneSelectorFunc | None = None

    def __init__(
        self,
        app: Quart | None = None,
        default_locale: str = DEFAULT_LOCALE,
        default_timezone: str = DEFAULT_TIMEZONE,
        date_formats: Quart | t.Dict = None,
        configure_jinja: bool = True,
        default_domain: Domain | None = None,
        locale_selector: LocaleSelectorFunc | None = None,
        timezone_selector: TimezoneSelectorFunc | None = None
    ) -> None:
        """
        Construct an instance of :class:`quart_babel.Babel`.

        Arguments:
            app: The Quart application to use. Defaults to ``None``.
            default_locale: The default locale to be used, defaults to 'en'.
            default_timezone: The default timezone to be used, defaults to
                'UTC'.
            date_formats: A mapping of Babel datetime form strings. Defaults
                to ``None``.
            configure_jinja: Sets if Jinja2 filters are added to the app.
                Defaults to ``True``.
            default_domain: The default translation domain. Defaults to
                ``None``.
            locale_selector: The custom locale selector. Defaults to ``None``.
            timezone_selector: The custom timezone selector. Defaults to
                ``None``.
        """
        if app is not None:
            self.init_app(
                app,
                default_locale,
                default_timezone,
                date_formats,
                configure_jinja,
                default_domain,
                locale_selector,
                timezone_selector
            )

    def init_app(
        self,
        app: Quart,
        default_locale: str = DEFAULT_LOCALE,
        default_timezone: str = DEFAULT_TIMEZONE,
        date_formats: t.Dict | None = None,
        configure_jinja: bool = True,
        default_domain: Domain | None = None,
        locale_selector: LocaleSelectorFunc | None = None,
        timezone_selector: TimezoneSelectorFunc | None = None
    ) -> None:
        """
        Initialize the Quart-Babel extension with the application.

        Arguments:
            app: The Quart application to use. Defaults to ``None``.
            default_locale: The default locale to be used, defaults to 'en'.
            default_timezone: The default timezone to be used, defaults to
                'UTC'.
            date_formats: A mapping of Babel datetime form strings. Defaults
                to ``None``.
            configure_jinja: Sets if Jinja2 filters are added to the app.
                Defaults to ``True``.
            default_domain: The default translation domain. Defaults to
                ``None``.
            locale_selector: The custom locale selector. Defaults to ``None``.
            timezone_selector: The custom timezone selector. Defaults to
                ``None``.
        """
        if default_domain is None:
            default_domain = Domain()

        app.config.setdefault('BABEL_DEFAULT_LOCALE', default_locale)
        app.config.setdefault('BABEL_DEFAULT_TIMEZONE', default_timezone)
        app.config.setdefault('BABEL_CONFIGURE_JINJA', configure_jinja)
        app.config.setdefault('BABEL_DOMAIN', default_domain)

        app.extensions['babel'] = BabelState(
            self, app, app.config['BABEL_DOMAIN']
        )

        if self.locale_selector is None and locale_selector is not None:
            self.locale_selector = locale_selector

        if self.timezone_selector is None and timezone_selector is not None:
            self.timezone_selector = timezone_selector

        #: a mapping of Babel datetime format strings that can be modified
        #: to change the defaults.  If you invoke :func:`format_datetime`
        #: and do not provide any format string Flask-Babel will do the
        #: following things:
        #:
        #: 1.   look up ``date_formats['datetime']``.  By default ``'medium'``
        #:      is returned to enforce medium length datetime formats.
        #: 2.   ``date_formats['datetime.medium'] (if ``'medium'`` was
        #:      returned in step one) is looked up.  If the return value
        #:      is anything but `None` this is used as new format string.
        #:      otherwise the default for that language is used.
        self.date_formats = date_formats or DEFAULT_DATE_FORMATS.copy()

        if app.config['BABEL_CONFIGURE_JINJA']:
            app.jinja_env.filters.update(
                datetimeformat=format_datetime,
                dateformat=format_date,
                timeformat=format_time,
                timedeltaformat=format_timedelta,

                numberformat=format_number,
                decimalformat=format_decimal,
                currencyformat=format_currency,
                percentformat=format_percent,
                scientificformat=format_scientific,
            )

            app.jinja_env.add_extension('jinja2.ext.i18n')

            app.jinja_env.install_gettext_callables(
                lambda x: self.translations.ugettext(x),
                lambda s, p, n: self.translations.ungettext(s, p, n),
                newstyle=True
            )

        app.asgi_app = QuartBabelMiddleware(
            app.asgi_app,
            app.config.get('BABEL_DEFAULT_LOCALE'),
            self.locale_selector,
            app.config.get('BABEL_DEFAULT_TIMEZONE'),
            self.timezone_selector
        )

    @property
    def translations(self) -> Translations:
        """
        Get the translations to use in the template. It will get the domain
        and return `Domain.translations`.
        """
        return get_domain().translations

    @staticmethod
    def load_locale(locale: str) -> Locale:
        """
        Load locale by name and cache it.

        Arguments:
            locale: String value of the locale.
        """
        state = get_state()
        value = state.locale_cache.get(locale)

        if value is None:
            state.locale_cache[locale] = value = convert_locale(locale)

        return value

    @property
    def default_locale(self) -> Locale:
        """
        The default locale from the configuration as instance of a
        `babel.Locale` object.
        """
        state = get_state()
        locale = state.app.config['BABEL_DEFAULT_LOCALE']
        return self.load_locale(locale)

    @property
    def default_timezone(self) -> BaseTzInfo:
        """
        The default timezone from the configuration as instance of a
        `pytz.BaseTzInfo` object.
        """
        state = get_state()
        timezone: str = state.app.config['BABEL_DEFAULT_TIMEZONE']
        return convert_timezone(timezone)

    @property
    def current_locale(self) -> Locale:
        """
        The current locale from context.
        """
        return get_locale()

    @property
    def current_language(self) -> str:
        """
        Returns the current language as a string
        using the current locale.
        """
        return self.current_locale.language

    @property
    def current_timezone(self) -> BaseTzInfo | None:
        """
        The current timezone from context.
        """
        return get_timezone()

    def list_translations(self) -> list:
        """
        Returns a list of all the locales translations exist for.  The
        list returned will be filled with actual locale objects and not just
        strings.
        """
        state = get_state()
        dirname = os.path.join(state.app.root_path, 'translations')

        if not os.path.isdir(dirname):
            return []

        result = []

        for folder in os.listdir(dirname):
            locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
            if not os.path.isdir(locale_dir):
                continue
            if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
                result.append(self.load_locale(folder))

        if not result:
            result.append(self.default_locale)

        return result
