"""
quart_babel.domain
"""
from __future__ import annotations
import os
from numbers import Number
import typing as t

from babel import support

from .locale import get_locale
from .speaklater import LazyString
from .typing import Translations
from .utils import get_state

if t.TYPE_CHECKING:
    from quart import Quart

__all__ = (
    'Domain',
    'get_domain',
    'gettext',
    'ngettext',
    'pgettext',
    'npgettext',
    'lazy_gettext',
    'lazy_ngettext',
    'lazy_pgettext'
)

class Domain:
    """
    Localization domain. By default it will look for tranlations in the
    Quart application directory and "messages" domain - all message
    catalogs should be called ``messages.mo``.
    """
    def __init__(
        self,
        dirname: str | os.PathLike[str] | None = None,
        domain: str = 'messages'
        ) -> None:
        """
        Construct a new instance of the :class:`Domain`.

        Arguments:
            dirname: The path to the directory for the domain. Defaults to ``None``.
            domain: The name of the domain. Defaults to ``'messages'``.
        """
        self.dirname = dirname
        self.domain = domain
        self.cache = {}

    @property
    def as_default(self) -> None:
        """
        Set this domain as the default one for the
        current request.
        """
        get_state().domain = self

    @property
    def translations_cache(self) -> dict:
        """
        Returns a dictionary like object for translation caching.
        """
        return self.cache

    def get_translations_path(self, app: Quart) -> str | os.PathLike[str]:
        """
        Returns the translations directory path. Override if you want
        to implement custom behavior.

        Arguments:
            app: The Quart application.
        """
        return self.dirname or os.path.join(app.root_path, 'translations')

    @property
    def translations(self) -> Translations:
        """
         Returns the correct gettext translations that should be used.
        This will never fail and return a dummy translation object if
        used outside of the app context or if a translation cannot be
        found.
        """
        state = get_state(silent=True)

        if state is None:
            return support.NullTranslations()

        locale = get_locale()
        cache = self.translations_cache

        translations = cache.get(str(locale))

        if translations is None:
            dirname = self.get_translations_path(state.app)

            translations = support.Translations.load(
                dirname,
                locale,
                self.domain
            )

            self.cache[str(locale)] = translations

        return translations

    def gettext(self, string: str, **variables) -> str:
        """
        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string:

            gettext('Hello World!')
            gettext('Hello %(name)s!', name='World')

        Arguments:
            string: The string to translate.
            variables:  kwargs for the translation.
        """
        translation = self.translations

        if variables:
            return translation.ugettext(string) % variables

        return translation.ugettext(string)

    def ngettext(self, singular: str, plural: str, num: Number, **variables) -> str:
        """
        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.  The source language should be
        English or a similar language which only has one plural form:

            ngettext('%(num)d Apple', '%(num)d Apples', num=len(apples))

        Arguments:
            singular: The singular string of the text.
            plural: the plural string of the text.
            num: The number parameter.
            variables: kwargs variables for the translation.
        """
        variables.setdefault('num', num)
        translation = self.translations

        return translation.ungettext(singular, plural, num) % variables

    def pgettext(self, context: str, string: str, **variables) -> str:
        """
        Like :func:`gettext` but with a context.

        Gettext uses the ``msgctxt`` notation to distinguish different
        contexts for the same ``msgid``

        For example::

            pgettext('Button label', 'Log in')

        Learn more about contexts here:
        https://www.gnu.org/software/gettext/manual/html_node/Contexts.html

        Arguments:
            context: The context to use.
            string: The string to use.
            variables: Kwargs variables for the translation.
        """
        translation = self.translations

        if variables:
            return translation.upgettext(context, string) % variables

        return translation.upgettext(context, string)

    def npgettext(
        self,
        context: str,
        singular: str,
        plural: str,
        num: Number,
        **variables
    ) -> str:
        """
        Like :func:`ngettext` but with a context.

        Arguments:
            context: The context to use.
            singular: The singular string of the text.
            plural: the plural string of the text.
            num: The number parameter.
            variables: Kwargs variables for the translation.
        """
        variables.setdefault('num', num)
        translation = self.translations

        return translation.unpgettext(context, singular, plural, num) % variables

    def lazy_gettext(self, string: str, **variables) -> LazyString:
        """
        Like :func:`gettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            hello = lazy_gettext('Hello World')

            @app.route('/')
            async def index():
                return hello

        Arguments:
            string: The string to translate.
            variables:  kwargs for the translation.
        """
        return LazyString(self.gettext, string, **variables)

    def lazy_ngettext(
        self, singular: str, plural: str, num: Number, **variables
    ) -> LazyString:
        """
        Like :func:`ngettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            a = lazy_ngettext('%(num)d Apple', '%(num)d Apples', num=len(a))

            @app.route('/')
            async def index():
                return a

        Arguments:
            singular: The singular string of the text.
            plural: the plural string of the text.
            num: The number parameter.
            variables: kwargs variables for the translation.
        """
        return LazyString(self.ngettext, singular, plural, num, **variables)

    def lazy_pgettext(
        self, context: str, string: str, **variables
    ) -> LazyString:
        """
        Like :func:`pgettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Arguments:
            context: The context to use.
            string: The string to use.
            variables: Kwargs variables for the translation.
        """
        return LazyString(self.pgettext, context, string, **variables)

# This is the domain that will be used if there is no request context
# and thus no app.
# It will also use this domain if the app isn't initialized for babel.
# Note that if there is no request context, then the standard
# Domain will use NullTranslations.
domain = Domain()

def get_domain() -> Domain:
    """
    Return the correct translation domain that is used for this request.

    This will return the default domain.

    Part of the internal API.

    e.g. "messages" in <approot>/translations" if none is set for this
    request.
    """
    state = get_state(silent=True)

    if state is None:
        return domain

    return state.domain

# Create shortcuts for the default Quart domain.
def gettext(string: str, **variables) -> str:
    """
    Shortcut to gettext for the default domain.

    Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string:

        gettext('Hello World!')
        gettext('Hello %(name)s!', name='World')

    Arguments:
        string: The string to translate.
        variables:  kwargs for the translation.
    """
    return get_domain().gettext(string, **variables)

_ = gettext

def ngettext(singular: str, plural: str, num: Number, **variables) -> str:
    """
    Shortcut to ngettext for the default domain.

    Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form:

        ngettext('%(num)d Apple', '%(num)d Apples', num=len(apples))

    Arguments:
        singular: The singular string of the text.
        plural: the plural string of the text.
        num: The number parameter.
        variables: kwargs variables for the translation.
    """
    return get_domain().ngettext(singular, plural, num, **variables)

def pgettext(context: str, string: str, **variables) -> str:
    """
    Shortcut to pgettext for the default domain.

    Like :func:`gettext` but with a context.

    Gettext uses the ``msgctxt`` notation to distinguish different
    contexts for the same ``msgid``

    For example::
        pgettext('Button label', 'Log in')

    Learn more about contexts here:
    https://www.gnu.org/software/gettext/manual/html_node/Contexts.html

    Arguments:
        context: The context to use.
        string: The string to use.
        variables: Kwargs variables for the translation.
    """
    return get_domain().pgettext(context, string, **variables)

def npgettext(
    context: str, singular: str, plural: str, num: Number, **variables
) -> str:
    """
    Shortcut to npgettext for the default domain.

    Arguments:
        context: The context to use.
        singular: The singular string of the text.
        plural: The plural string of the text.
        num: The number parameter.
        variables: Kwargs variables for the translation.
    """
    return get_domain().npgettext(context, singular, plural, num, **variables)

def lazy_gettext(string: str, **variables) -> LazyString:
    """
    Lazy gettext shorcut for the default domain.

    Like :func:`gettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        hello = lazy_gettext('Hello World')

        @app.route('/')
        async def index():
            return hello

    Arguments:
        string: The string to translate.
        variables:  kwargs for the translation.
    """
    return LazyString(gettext, string, **variables)

def lazy_ngettext(singular: str, plural: str, num: Number, **variables) -> LazyString:
    """
    Lazy ngettext shorcut for the default domain.

    Like :func:`ngettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        a = lazy_ngettext('%(num)d Apple', '%(num)d Apples', num=len(a))

        @app.route('/')
        async def index():
            return a

    Arguments:
        context: The context to use.
        singular: The singular string of the text.
        plural: The plural string of the text.
        num: The number parameter.
        variables: Kwargs variables for the translation.
    """
    return LazyString(ngettext, singular, plural, num, **variables)

def lazy_pgettext(context: str, string: str, **variables) -> LazyString:
    """
    Lazy pgettext shorcut for the default domain.

    Like :func:`pgettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Arguments:
        context: The context to use.
        singular: The string of the text.
        variables: Kwargs variables for the translation.
    """
    return LazyString(pgettext, context, string, **variables)
