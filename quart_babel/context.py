"""
quart_babel.context
"""
from contextvars import ContextVar, Token

from .typing import Locale, BaseTzInfo
from .utils import convert_locale, convert_timezone


class LocaleStorageContext:
    """
    Locale Context Storage for Quart Babel.

    This class is used to store the locale
    context. It also provides functions to
    work with the context variable.

    Part of the internal API.
    """
    CONTEXT_KEY_NAME = "current_locale"

    def __init__(self) -> None:
        """
        Construct an instance of the Locale Context Storage.
        """
        self._default_locale: Locale | None = None
        self._values: ContextVar[Locale] | None = None
        self._token_id: Token[Locale] | None = None

    @property
    def default_locale(self) -> Locale:
        """
        Default locale as a `babel.Locale` object. If the
        default value is ``None`` it will raise a `ValueError`
        """
        if self._default_locale is None:
            raise ValueError('The default locale is not set.')
        return self._default_locale

    def setup_context(self, default_locale: Locale | str) -> None:
        """
        Setup the current locale context variable.

        This method is used to pass the default locale from the app
        to set as the default in the context variable by
        :class:`QuartBabelMiddleware`. It will then setup the context
        variable.

        Arguments:
            default_locale: The default locale to use.
        """
        self._default_locale = convert_locale(default_locale)
        self._values = ContextVar(
            self.CONTEXT_KEY_NAME, default=self._default_locale
            )

    def get(self) -> Locale:
        """
        Gets the current locale from context.
        """
        return self._values.get()

    def set(self, value: Locale | str) -> None:
        """
        Sets the current locale to context. It will
        check to see what value type is provided by
        using the function `quart_babel.utils.convert_locale`.

        Arguments:
            value: The locale to set.

        """
        value = convert_locale(value)
        self._token_id = self._values.set(value)

    def refresh(self, value: Locale | str | None = None) -> None:
        """
        Refreshes the current locale.

        This is used to set the context to specifc locale before the
        request. If a value is provided, it will check the type using
        `quart_babel.utils.convert_locale`. If not value is provided,
        it will set the context to the default locale.

        Arguments:
            value: The value to set the locale.
        """
        if value:
            value = convert_locale(value)
            self.set(value)
        else:
            self.set(self.default_locale)


class TimezoneStorageContext:
    """
    Timezone Context Storage for Quart Babel.

    This class is ued to store the timezone context.
    It also provides functions to work with the context
    variable.

    Part of the internal API.
    """
    CONTEXT_KEY_NAME = "current_timezone"

    def __init__(self) -> None:
        """
        Construct an instance of Timezone Storage Context.
        """
        self._default_timezone: BaseTzInfo | None = None
        self._values: ContextVar[BaseTzInfo] | None = None
        self._token_id: Token[BaseTzInfo] | None = None

    @property
    def default_timezone(self) -> BaseTzInfo:
        """
        Default timezone as a `pytz.BaseTzInfo` object.
        If the default value is ``None`` it will raise
        a `ValueError`
        """
        if self._default_timezone is None:
            raise ValueError('Default timezone is not set.')
        return self._default_timezone

    def setup_context(self, default_timezone: BaseTzInfo | str) -> None:
        """
        Setup the current timezone context variable.

        This method is used to pass the default timezone from the app
        to set as the default in the context variable by
        `QuartBabelMiddleware`. It will then setup the context variable.

        Arguments:
            default_timezone: The default timezone to use.
        """
        self._default_timezone = convert_timezone(default_timezone)
        self._values = ContextVar(
            self.CONTEXT_KEY_NAME, default=self._default_timezone
            )

    def get(self) -> BaseTzInfo:
        """
        Gets the current timezone from context.
        """
        return self._values.get()

    def set(self, value: BaseTzInfo | str) -> None:
        """
        Sets the current timezone to context. It will
        check to see what value is provided by using the
        function `quart_babel.utils.convert_locale`.

        Arguments:
            value: The timezone to set.
        """
        value = convert_timezone(value)
        self._token_id = self._values.set(value)

    def refresh(self, value: BaseTzInfo | str | None = None) -> None:
        """
        Refreshes the current timezone.

        This is used to set the context to specifc timezone before the
        request. If a value is provided, it will check the type using
        `quart_babel.utils.convert_timezone`. If not value is provided,
        it will set the context to the default timezone.

        Arguments:
            value: The value to set the timezone.
        """
        if value:
            value = convert_timezone(value)
            self.set(value)
        else:
            self.set(self.default_timezone)
