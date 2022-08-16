"""
    quart_babel.domain
    ~~~~~~~~~~~~~~~~~~~~~~
    Localization domain.
    :copyright: (c) 2013 by Armin Ronacher, Daniel Neuhäuser and contributors.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations
import os
from numbers import Number
from typing import Optional, Union, TYPE_CHECKING
from babel import support
from quart import Quart

from .speaklater import LazyString
from .utils import get_state
from .utils import get_locale

if TYPE_CHECKING:
    from .core import _BabelState

__all__ = (
    'Domain',
    'get_domain',
    'gettext',
    'lazy_gettext',
    'lazy_ngettext',
    'lazy_pgettext',
    'ngettext',
    'npgettext',
    'pgettext'
)

class Domain(object):
    """Localization domain. By default it will look for tranlations in the
    Quart application directory and "messages" domain - all message
    catalogs should be called ``messages.mo``.
    """

    def __init__(self, dirname: Optional[str]=None, domain: str='messages') -> None:
        self.dirname: Optional[str]= dirname
        self.domain: str = domain

        self.cache = {}

    def as_default(self):
        """Set this domain as the default one for the current request"""
        get_state().domain = self

    def get_translations_cache(self) -> dict:
        """Returns a dictionary-like object for translation caching"""
        return self.cache

    def get_translations_path(self, app: Quart) -> str:
        """Returns the translations directory path. Override if you want
        to implement custom behavior.
        """
        return self.dirname or os.path.join(app.root_path, 'translations')

    async def get_translations(self) -> Union[support.Translations, support.NullTranslations]:
        """Returns the correct gettext translations that should be used for
        this request.  This will never fail and return a dummy translation
        object if used outside of the request or if a translation cannot be
        found.
        """
        state: _BabelState = get_state(silent=True)

        if state is None:
            return support.NullTranslations()

        locale = await get_locale()
        cache = self.get_translations_cache()

        translations = cache.get(str(locale))
        if translations is None:
            dirname = self.get_translations_path(state.app)
            translations = support.Translations.load(
                dirname,
                locale,
                domain=self.domain
            )
            self.cache[str(locale)] = translations

        return translations

    async def gettext(self, string: str, **variables) -> str:
        """Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.::

            gettext('Hello World!')
            gettext('Hello %(name)s!', name='World')

        """
        val = await self.get_translations()
        if variables:
            return val.ugettext(string) % variables
        return val.ugettext(string)

    async def ngettext(self, singular: str, plural: str, num: Number, **variables) -> str:
        """Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.  The source language should be
        English or a similar language which only has one plural form.::

            ngettext('%(num)d Apple', '%(num)d Apples', num=len(apples))

        """
        variables.setdefault('num', num)
        val = await self.get_translations()
        return val.ungettext(singular, plural, num) % variables

    async def pgettext(self, context: str, string: str, **variables) -> str:
        """Like :func:`gettext` but with a context.

        Gettext uses the ``msgctxt`` notation to distinguish different
        contexts for the same ``msgid``

        For example::

            pgettext('Button label', 'Log in')

        Learn more about contexts here:
        https://www.gnu.org/software/gettext/manual/html_node/Contexts.html
        """
        val = await self.get_translations()
        if variables:
            return val.upgettext(context, string) % variables
        return val.upgettext(context, string)

    async def npgettext(
        self, context: str,
        singular: str,
        plural: str,
        num: Number,
        **variables
        ) -> str:
        """Like :func:`ngettext` but with a context.
        """
        variables.setdefault('num', num)
        val = await self.get_translations()
        return val.unpgettext(context, singular, plural, num) % variables

    def lazy_gettext(self, string: str, **variables) -> LazyString:
        """Like :func:`gettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            hello = lazy_gettext('Hello World')
            @app.route('/')
            async def index():
                return unicode(await hello)

        """
        return LazyString(self.gettext, string, **variables)

    async def lazy_ngettext(
        self,
        singular: str,
        plural: str,
        num: Number,
        **variables
        ) -> LazyString:
        """Like :func:`ngettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            a = lazy_ngettext('%(num)d Apple', '%(num)d Apples', num=len(a))
            @app.route('/')
            async def index():
                return unicode(await a)

        """
        return LazyString(self.ngettext, singular, plural, num, **variables)

    def lazy_pgettext(self, context: str, string: str, **variables) -> LazyString:
        """Like :func:`pgettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.
        """
        return LazyString(self.pgettext, context, string, **variables)


# This is the domain that will be used if there is no request context
# and thus no app.
# It will also use this domain if the app isn't initialized for babel.
# Note that if there is no request context, then the standard
# Domain will use NullTranslations.
domain = Domain()


def get_domain() -> Domain:
    """Return the correct translation domain that is used for this request.
    This will return the default domain
    e.g. "messages" in <approot>/translations" if none is set for this
    request.
    """
    state: _BabelState = get_state(silent=True)
    if state is None:
        return domain

    return state.domain


# Create shortcuts for the default Quart domain

async def gettext(*args, **kwargs) -> str:
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.::

            gettext('Hello World!')
            gettext('Hello %(name)s!', name='World')

    """
    domain = get_domain()
    return await domain.gettext(*args, **kwargs)

_ = gettext  # noqa

async def ngettext(*args, **kwargs) -> str:
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form.::

        ngettext('%(num)d Apple', '%(num)d Apples', num=len(apples))

    """
    domain = get_domain()
    return await domain.ngettext(*args, **kwargs)

async def pgettext(*args, **kwargs) -> str:
    """Like :func:`gettext` but with a context.
    Gettext uses the ``msgctxt`` notation to distinguish different
    contexts for the same ``msgid``

    For example::

        pgettext('Button label', 'Log in')

    Learn more about contexts here:
    https://www.gnu.org/software/gettext/manual/html_node/Contexts.html
    """
    domain = get_domain()
    return await domain.pgettext(*args, **kwargs)

async def npgettext(*args, **kwargs) -> str:
    """Like :func:`ngettext` but with a context.
    """
    domain = get_domain()
    return await domain.npgettext(*args, **kwargs)

def lazy_gettext(*args, **kwargs) -> LazyString:
    """Like :func:`gettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        hello = lazy_gettext('Hello World')
        @app.route('/')
        async def index():
            return unicode(await hello)
    """
    return LazyString(gettext, *args, **kwargs)

def lazy_ngettext(*args, **kwargs) -> LazyString:
    """Like :func:`ngettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        a = lazy_ngettext('%(num)d Apple', '%(num)d Apples', num=len(a))
        @app.route('/')
        async def index():
            return unicode(await a)

    """
    return LazyString(ngettext, *args, **kwargs)

def lazy_pgettext(*args, **kwargs) -> LazyString:
    """Like :func:`pgettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.
    """
    return LazyString(pgettext, *args, **kwargs)
