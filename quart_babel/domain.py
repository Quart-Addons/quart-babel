"""
quart_babel.domain
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Type, Tuple, Union

from babel import support
from babel.support import Translations, NullTranslations

from .locale import get_locale
from .speaklater import LazyString
from .utils import get_babel, _get_current_context


class Domain:
    """
    Localization domain. By default, it will look for translations in the
    Quart application directory and "messages" domain - all message catalogs
    should be called ``messages.mo``.

    Additional domains are supported passing a list of domain names to the
    ``domain`` argument, but note that in this case they must match a list
    passed to ``translation_directories``, eg::

        Domain(
            translation_directories=[
                "/path/to/translations/with/messages/domain",
                "/another/path/to/translations/with/another/domain",
            ],
            domains=[
                "messages",
                "myapp",
            ]
        )
    """
    def __init__(
            self,
            translation_directories: Optional[Union[str, List[str]]] = None,
            domain: Union[str, List[str]] = 'messages'
    ) -> None:
        if isinstance(translation_directories, str):
            translation_directories = [translation_directories]
        self._translation_directories = translation_directories

        if isinstance(domain, str):
            self.domain = [domain]
        else:
            self.domain = domain

        self.cache: Dict[Tuple[str, str], Translations] = {}

    def __repr__(self) -> str:
        return f"<Domain({self._translation_directories}, {self.domain})>"

    @property
    def translation_directories(self) -> List[str]:
        """
        Returns the translation directories.
        """
        if self._translation_directories is not None:
            return self._translation_directories
        return get_babel().translation_directories

    def as_default(self) -> None:
        """
        Set this domain as default for the current request.
        """
        ctx = _get_current_context()

        if ctx is None:
            raise RuntimeError("No request context.")

        ctx.babel_domain = self

    def get_translations_cache(self) -> Dict[Tuple[str, str], Translations]:
        """
        Returns dictionary-like object for translation caching.
        """
        return self.cache

    def get_translations(self) -> Union[NullTranslations, Translations]:
        """
        Gets the translations for the Domain.
        """
        ctx = _get_current_context()

        if ctx is None:
            return support.NullTranslations()

        cache = self.get_translations_cache()
        locale = get_locale()

        try:
            return cache[str(locale), self.domain[0]]
        except KeyError:
            translations = support.Translations()

            for index, dirname in enumerate(self.translation_directories):

                domain = self.domain[0] if len(self.domain) == 1 \
                    else self.domain[index]

                catalog = support.Translations.load(dirname, [locale], domain)
                translations.merge(catalog)
                # FIXME: Workaround for merge() being really, really stupid. It
                # does not copy _info, plural(), or any other instance variables
                # populated by GNUTranslations. We probably want to stop using
                # `support.Translations.merge` entirely.
                if catalog.info() and hasattr(catalog, "plural"):
                    translations.plural = catalog.plural

        cache[str(locale), self.domain[0]] = translations
        return translations

    def gettext(self, string: str, **variables: Any) -> str:
        """
        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.

        ::

            gettext(u'Hello World!')
            gettext(u'Hello %(name)s!', name='World')
        """
        t = self.get_translations()
        s = t.ugettext(string)
        return s if not variables else s % variables

    def ngettext(
            self, singular: str, plural: str, num: int, **variables: Any
    ) -> str:
        """
        ranslates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.  The source language should be
        English or a similar language which only has one plural form.

        ::

            ngettext(u'%(num)d Apple', u'%(num)d Apples', num=len(apples))
        """
        variables["num"] = num
        t = self.get_translations()
        s = t.ungettext(singular, plural, num)
        return s if not variables else s % variables

    def pgettext(self, context: str, string: str, **variables: Any) -> str:
        """
        Like :func:`gettext` but with a context.
        """
        t = self.get_translations()
        s = t.upgettext(context, string)
        return s if not variables else s % variables

    def npgettext(
            self,
            context: str,
            singular: str,
            plurarl: str,
            num: int,
            **variables: Any
    ) -> str:
        """
        Like :func:`ngettext` but with a context.
        """
        variables["num"] = num
        t = self.get_translations()
        s = t.unpgettext(context, singular, plurarl, num)
        return s if not variables else s % variables

    def lazy_gettext(self, string: str, **variables: Any) -> LazyString:
        """
        Like :func:`gettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            hello = lazy_gettext(u'Hello World')

            @app.route('/')
            def index():
                return unicode(hello)
        """
        return LazyString(self.gettext, string, **variables)

    def lazy_ngettext(
            self, singular: str, plural: str, num: int, **variables: Any
    ) -> LazyString:
        """
        Like :func:`ngettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            apples = lazy_ngettext(
                u'%(num)d Apple',
                u'%(num)d Apples',
                num=len(apples)
            )

            @app.route('/')
            def index():
                return unicode(apples)
        """
        return LazyString(self.ngettext, singular, plural, num, **variables)

    def lazy_pgettext(
            self, context: str, string: str, **variables: Any
    ) -> LazyString:
        """
        Like :func:`pgettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.
        """
        return LazyString(self.pgettext, context, string, **variables)


def get_domain() -> Domain:
    """
    Gets the current `Domain`.
    """
    ctx = _get_current_context()

    if ctx is None:
        # this will use NullTranslations
        return Domain()

    try:
        return ctx.babel_domain
    except AttributeError:
        pass

    ctx.babel_domain = get_babel().instance.domain_instance
    return ctx.babel_domain


def get_translations() -> Union[Translations, Type[NullTranslations]]:
    """
    Returns the correct gettext translations that should be used for
    this request.  This will never fail and return a dummy translation
    object if used outside the request or if a translation cannot be found.
    """
    return get_domain().get_translations()


# Create shortcuts for the default Quart domain
def gettext(*args: str, **kwargs: Any) -> str:
    """
    Shortcut to :func:`gettext` for the default Quart
    domain.
    """
    return get_domain().gettext(*args, **kwargs)


_ = gettext


def ngettext(*args: Any, **kwargs: Any) -> str:
    """
    Shortcut to :func:`ngettext` for the default Quart
    domain.
    """
    return get_domain().ngettext(*args, **kwargs)


def pgettext(*args: str, **kwargs: Any) -> str:
    """
    Shortcut to :func:`pgettext` for the default Quart
    domain.
    """
    return get_domain().pgettext(*args, **kwargs)


def npgettext(*args: Any, **kwargs: Any) -> str:
    """
    Shortcut to :func:`npgettext` for the default Quart
    domain.
    """
    return get_domain().npgettext(*args, **kwargs)


def lazy_gettext(*args: str, **kwargs: Any) -> LazyString:
    """
    Shortcut to :func:`gettext` for a :class:`LazyString` using
    the default Quart domain.

    Returns:
        `LazyString`.
    """
    return LazyString(gettext, *args, **kwargs)


def lazy_ngettext(*args: Any, **kwargs: Any) -> LazyString:
    """
    Shortcut to :func:`ngettext` for a :class:`LazyString` using
    the default Quart domain.

    Returns:
        `LazyString`.
    """
    return LazyString(ngettext, *args, **kwargs)


def lazy_pgettext(*args: str, **kwargs: Any) -> LazyString:
    """
    Shortcut to :func:`pgettext` for a :class:`LazyString` using
    the default Quart domain.

    Returns:
        `LazyString`.
    """
    return LazyString(pgettext, *args, **kwargs)


def lazy_npgettext(*args: Any, **kwargs: Any) -> LazyString:
    """
    Shortcut to :func:`npgettext` for a :class:`LazyString` using
    the default Quart domain.

    Returns:
        `LazyString`.
    """
    return LazyString(npgettext, *args, **kwargs)
