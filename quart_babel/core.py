"""
    quart_babel.core
    ~~~~~~~~~~~~~~~~~~~~~
    The actual Quart extension.
    :copyright: (c) 2013 by Armin Ronacher, Daniel Neuhäuser and contributors.
    :license: BSD, see LICENSE for more details.
"""
import os
import asyncio
from typing import Callable, List, Optional, Union
from dataclasses import dataclass, field

import nest_asyncio
from babel import Locale, support
from pytz import timezone
from quart import Quart

from .constants import DEFAULT_DATE_FORMATS, DEFAULT_LOCALE, DEFAULT_TIMEZONE
from .domain import Domain, get_domain
from .utils.context import get_state
from .utils.formats import (format_currency, format_date, format_datetime, format_decimal,
                            format_number, format_percent, format_scientific, format_time,
                            format_timedelta)

__all__ = ('Babel', '_BabelState')

class Babel(object):
    """Central controller class that can be used to configure how
    Flask-Babel behaves.  Each application that wants to use Flask-Babel
    has to create, or run :meth:`init_app` on, an instance of this class
    after the configuration was initialized.
    """

    def __init__(
        self, app: Optional[Quart]=None,
        default_locale: str=DEFAULT_LOCALE,
        default_timezone: str=DEFAULT_TIMEZONE,
        date_formats: Optional[dict]=None,
        configure_jinja: bool=True,
        default_domain: Optional[Domain]=None,
        ipapi_key: Optional[str]=None,
        nest_async: bool = True
        ) -> None:
        """Initializes the Quart-Babel extension.
        :param app: The Quart application.
        :param kwargs: Optional arguments that will be passed to ``init_app``.
        """
        self.app = app
        self.loop = None
        self.locale_selector_func: Optional[Callable] = None
        self.timezone_selector_func: Optional[Callable] = None

        if app is not None:
            self.init_app(
                app,
                default_locale,
                default_timezone,
                date_formats,
                configure_jinja,
                default_domain,
                ipapi_key,
                nest_async
                )

    def init_app(
        self,
        app: Quart,
        default_locale: str=DEFAULT_LOCALE,
        default_timezone: str=DEFAULT_TIMEZONE,
        date_formats: Optional[dict]=None,
        configure_jinja: bool=True,
        default_domain: Optional[Domain]=None,
        ipapi_key: Optional[str]=None,
        nest_async: bool= True
        ) -> None:
        """Initializes the Quart-Babel extension.

        :param app: The Quart application.
        :param default_locale: The default locale which should be used. Defaults to 'en'.
        :param default_timezone: The default timezone. Defaults to 'UTC'.
        :param date_formats: A mapping of Babel datetime format strings
        :param configure_jinja: If set to ``True`` some convenient jinja2
                                filters are being added.
        :param default_domain: The default translation domain.
        :param ipapi_key: The IP API key to use.
        :param nest_async: To deactivate `nest_asyncio` module.
        """
        if default_domain is None:
            default_domain = Domain()

        app.config.setdefault('BABEL_DEFAULT_LOCALE', default_locale)
        app.config.setdefault('BABEL_DEFAULT_TIMEZONE', default_timezone)
        app.config.setdefault('BABEL_CONFIGURE_JINJA', configure_jinja)
        app.config.setdefault('BABEL_DOMAIN', default_domain)
        app.config.setdefault('BABEL_IPAPI_KEY', ipapi_key)
        app.config.setdefault('BABEL_NESTED_ASYNCIO', nest_asyncio)

        app.extensions['babel'] = _BabelState(babel=self, app=app,
                                              domain=default_domain)

        if nest_async:
            nest_asyncio.apply()

        app.before_serving(self._get_loop)

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

        if configure_jinja:
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
                lambda x: self._get_translations.ugettext(x),
                lambda s, p, n: self._get_translations.ungettext(s, p, n),
                newstyle=True
            )

    async def _get_loop(self) -> None:
        """
        This function is called by `Quart` prior to serving to get the existing
        `asyncio` event loop and saves it into the function.
        """
        self.loop = asyncio.get_event_loop()

    @property
    def _get_translations(self) -> Union[support.Translations, support.NullTranslations]:
        """
        Gets the translations to use in the template. Note that ``Domain.get_translations``
        is a coroutine. Since, we can't run the function directly with ``await`` since we
        are not in an async function when called by `Babel.init_app` we need to run with
        `asyncio.loop.run_until_complete`.
        """
        domain = get_domain()
        return self.loop.run_until_complete(domain.get_translations())

    def localeselector(self, func: Callable) -> Callable:
        """Registers a callback function for locale selection.  The default
        behaves as if a function was registered that returns `None` all the
        time.  If `None` is returned, the locale falls back to the one from
        the configuration.
        This has to return the locale as string (eg: ``'de_AT'``, ''`en_US`'')
        """
        self.locale_selector_func = func
        return func

    def timezoneselector(self, func: Callable) -> Callable:
        """Registers a callback function for timezone selection.  The default
        behaves as if a function was registered that returns `None` all the
        time.  If `None` is returned, the timezone falls back to the one from
        the configuration.
        This has to return the timezone as string (eg: ``'Europe/Vienna'``)
        """
        self.timezone_selector_func = func
        return func

    def list_translations(self) -> List:
        """Returns a list of all the locales translations exist for.  The
        list returned will be filled with actual locale objects and not just
        strings.
        """
        # Wouldn't it be better to list the locales from the domain?
        state: _BabelState = get_state()
        dirname = os.path.join(state.app.root_path, 'translations')
        if not os.path.isdir(dirname):
            return []
        result = []
        for folder in os.listdir(dirname):
            locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
            if not os.path.isdir(locale_dir):
                continue
            if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
                result.append(Locale.parse(folder))
        if not result:
            result.append(Locale.parse(self.default_locale))
        return result

    @property
    def default_locale(self) -> Locale:
        """The default locale from the configuration as instance of a
        `babel.Locale` object.
        """
        state: _BabelState = get_state()
        return self.load_locale(state.app.config['BABEL_DEFAULT_LOCALE'])

    @property
    def default_timezone(self):
        """The default timezone from the configuration as instance of a
        `pytz.timezone` object.
        """
        state: _BabelState = get_state()
        return timezone(state.app.config['BABEL_DEFAULT_TIMEZONE'])

    def load_locale(self, locale: str) -> Locale:
        """Load locale by name and cache it. Returns instance of a
        `babel.Locale` object.
        """
        state: _BabelState = get_state()
        return_val = state.locale_cache.get(locale)
        if return_val is None:
            state.locale_cache[locale] = return_val = Locale.parse(locale)
        return return_val

@dataclass
class _BabelState:
    """
    Class for holding the state for Babel.
    """
    babel: Babel
    app: Quart
    domain: Domain
    locale_cache: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f'<_BabelState({self.babel}, {self.app}, {self.domain})>'
