.. _selectfunc:

==================
Selector Functions
==================

Selector functions allow you to provide away to determine a user's locale
and timezone based on pre-existing information in an application. These
functions can be set on the constructor of `~Babel` object, when initializing
the app with the babel extension; `~Babel.init_app`, or by directly setting
`~Babel.locale_selector` and/or `~Babel.timezone_selector`. These functions
are then passed to the constructor for `~QuartBabelMiddleware`. 

If any of these methods return `None` the extension will automatically
fall back to what's in the config.  If you need to switch the language 
or timezone between a request, you can :func:`refresh_locale` and
:func:`refresh_timezone` respectively.

The selector functions must be coroutines.

Locale Selector:
----------------

The locale selector must accept an ASGI request object, which is different
`~Quart.request`. The `~QuartBabelMiddleware` will pass the ASGI request
object to the locale selector function when called. Furthermore, the locale
selector needs to return a string or `Babel.Locale` object.

You can also call use :func:`select_locale_by_request` to fallback on if no
information is available.

.. code-block:: python
    :caption: Locale Selector Example

    from quart import Quart, g, request
    from quart_babel import Babel, select_locale_by_request
    from quart_babel.typing import ASGIRequest

    app = Quart(__name__)

    async def get_locale(request: ASGIRequest) -> str:
       # if a user is logged in, use the locale from the user settings
       user = getattr(g, 'user', None)
       if user is not None:
           return user.locale
       # otherwise select the user by the ASGI request object.
       return await select_locale_by_request(request)

    babel(app, locale_selector=get_locale)

Timezone Selector:
------------------

The timezone selector must accept an ASGI request object, which is different
`~Quart.request`. The `~QuartBabelMiddleware` will pass the ASGI request
object to the locale selector function when called. Furthermore, the locale
selector needs to return a string.

You can also call use :func:`select_timezone_by_request` to fallback on if no
information is available.

.. code-block:: python
    :caption: Timezone Selector Example

    import asyncio
    from quart import Quart, g, request
    from quart_babel import Babel, select_locale_by_request
    from quart_babel.typing import ASGIRequest

    app = Quart(__name__)

    async def get_timezone(request: ASGIRequest) -> str | None:
       # if a user is logged in, use the locale from the user settings
       user = getattr(g, 'user', None)
       if user is not None:
           return user.timezone
       # otherwise use default timezone by returning None.
       return None

    babel(app, timezone_selector=get_timezone)

.. note::
    The examples above assumes that the current user is stored on the
    :data:`Quart.g` object.
