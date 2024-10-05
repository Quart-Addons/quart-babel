"""
quart_babel.core
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from babel import Locale
from quart import Quart
from pytz import BaseTzInfo, timezone
from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import cached_property

from .domain import Domain, get_translations

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

from .utils import get_babel


@dataclass
class BabelConfiguration:
    """
    Application configuration for
    Babel.
    """
    default_locale: str
    default_timezone: str
    default_domain: Union[str, List[str]]
    default_directories: List[str]
    translation_directories: List[str]

    instance: Babel

    locale_selector: Optional[Callable] = None
    timezone_selector: Optional[Callable] = None


class Babel:
    """
    Central controller class that can be used to configure how
    Quart-Babel behaves.  Each application that wants to use Quart-Babel
    has to create, or run :meth:`init_app` on, an instance of this class
    after the configuration was initialized.
    """

    default_date_formats = ImmutableDict(
        {
            "time": "medium",
            "date": "medium",
            "datetime": "medium",
            "time.short": None,
            "time.medium": None,
            "time.full": None,
            "time.long": None,
            "date.short": None,
            "date.medium": None,
            "date.full": None,
            "date.long": None,
            "datetime.short": None,
            "datetime.medium": None,
            "datetime.full": None,
            "datetime.long": None,
        }
    )

    def __init__(
            self,
            app: Optional[Quart] = None,
            date_formats: Optional[Dict[str, Any]] = None,
            configure_jinja: bool = True,
            default_locale: str = 'en',
            default_domain: str = 'messages',
            default_translation_directories: Union[str, List[str]] = 'translations',
            default_timezone: str = 'UTC',
            locale_selector: Optional[Callable] = None,
            timezone_selector: Optional[Callable] = None
    ) -> None:
        """
        Creates a new Babel instance.

        If an application is passed, it will be configured with the provided
        arguments. Otherwise, :meth:`init_app` can be used to configure the
        application later.
        """
        self._configure_jinja = configure_jinja
        self.date_formats = date_formats

        if app is not None:
            self.init_app(
                app,
                default_locale,
                default_domain,
                default_translation_directories,
                default_timezone,
                locale_selector,
                timezone_selector
            )

    def init_app(
            self,
            app: Quart,
            default_locale: str = 'en',
            default_domain: str = 'messages',
            default_translation_directories: Union[str, List[str]] = 'translations',
            default_timezone: str = 'UTC',
            locale_selector: Optional[Callable] = None,
            timezone_selector: Optional[Callable] = None
    ) -> None:
        """
        Initializes the Babel instance for use with this specific application.

        :param app: The application to configure
        :param default_locale: The default locale to use for this application
        :param default_domain: The default domain to use for this application
        :param default_translation_directories: The default translation
                                                directories to use for this
                                                application
        :param default_timezone: The default timezone to use for this
                                 application
        :param locale_selector: The function to use to select the locale
                                for a request
        :param timezone_selector: The function to use to select the
                                  timezone for a request
        """
        if isinstance(default_translation_directories, str):
            default_translation_directories = [default_translation_directories]

        directories = app.config.get(
            'BABEL_TRANSLATION_DIRECTORIES', default_translation_directories
        )

        if isinstance(directories, str):
            directories = [directories]

        app.extensions['babel'] = BabelConfiguration(
            default_locale=app.config.get(
                "BABEL_DEFAULT_LOCALE", default_locale
            ),
            default_timezone=app.config.get(
                "BABEL_DEFAULT_TIMEZONE", default_timezone
            ),
            default_domain=app.config.get('BABEL_DOMAIN', default_domain),
            default_directories=directories,
            translation_directories=list(
                self._resolve_directories(directories, app=app)
            ),
            instance=self,
            locale_selector=locale_selector,
            timezone_selector=timezone_selector
        )

        # a mapping of Babel datetime format strings that can be modified
        # to change the defaults.  If you invoke :func:`format_datetime`
        # and do not provide any format string Flask-Babel will do the
        # following things:
        #
        # 1.   look up ``date_formats['datetime']``.  By default, ``'medium'``
        #      is returned to enforce medium length datetime formats.
        # 2.   ``date_formats['datetime.medium'] (if ``'medium'`` was
        #      returned in step one) is looked up.  If the return value
        #      is anything but `None` this is used as new format string.
        #      otherwise the default for that language is used.
        if self.date_formats is None:
            self.date_formats = self.default_date_formats.copy()

        if self._configure_jinja:
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
            app.jinja_env.add_extension("jinja2.ext.i18n")
            app.jinja_env.install_gettext_callables(
                gettext=lambda s: get_translations().ugettext(s),
                ngettext=lambda s, p, n: get_translations().ungettext(s, p, n),
                newstyle=True,
                pgettext=lambda c, s: get_translations().upgettext(c, s),
                npgettext=lambda c, s, p, n: get_translations().unpgettext(c, s, p, n),
            )

    def list_translations(self) -> List[Locale]:
        """
        Returns a list of all the locales translations exist for. The list
        returned will be filled with actual locale objects and not just
        strings.

        .. note::

            The default locale will always be returned, even if no translation
            files exist for it.
        """
        result = []

        for dirname in get_babel().translation_directories:
            if not os.path.isdir(dirname):
                continue

            for folder in os.listdir(dirname):
                locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
                if not os.path.isdir(locale_dir):
                    continue

                if any(x.endswith(".mo") for x in os.listdir(locale_dir)):
                    result.append(Locale.parse(folder))

        if self.default_locale not in result:
            result.append(self.default_locale)

        return result

    @property
    def default_locale(self) -> Locale:
        """
        The default locale from the configuration as an instance of a
        `babel.Locale` object.
        """
        return Locale.parse(get_babel().default_locale)

    @property
    def default_timezone(self) -> BaseTzInfo:
        """
        The default timezone from the configuration as an instance of a
        `pytz.timezone` object.
        """
        return timezone(get_babel().default_timezone)

    @property
    def domain(self) -> Union[str, List[str]]:
        """
        The message domain for the translations as a string
        """
        return get_babel().default_domain

    @cached_property
    def domain_instance(self) -> Domain:
        """
        The message domain for the translations.
        """
        return Domain(domain=self.domain)

    @staticmethod
    def _resolve_directories(
        directories: List[str], app: Optional[Quart] = None
    ) -> Generator[str, Any, None]:
        for path in directories:
            if os.path.isabs(path):
                yield path
            elif app is not None:
                # We can only resolve relative paths if we have an
                # application context.
                yield os.path.join(app.root_path, path)
