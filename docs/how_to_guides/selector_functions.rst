.. _selectfunc:

==================
Selector Functions
==================

For more complex applications you might want to have multiple applications
for different users which is where selector functions come in handy.  The
first time the babel extension needs the locale (language code) of the
current user it will call a :meth:`~Babel.localeselector` function, and
the first time the timezone is needed it will call a
:meth:`~Babel.timezoneselector` function.

If any of these methods return `None` the extension will automatically
fall back to what's in the config.  Furthermore for efficiency that
function is called only once and the return value then cached.  If you
need to switch the language between a request, you can :func:`refresh` the
cache.

Quart Babel allows the selector functions to be async or sync. If they are
sync. They will be wrapped in :func:`run_sync`. 

Examples of selector functions:

.. code-block:: python
    :caption: Sync Code

    from quart import g, request

    @babel.localeselector
    def get_locale():
       # if a user is logged in, use the locale from the user settings
       user = getattr(g, 'user', None)
       if user is not None:
           return user.locale
       # otherwise try to guess the language from the user accept
       # header the browser transmits.  We support de/fr/en in this
       # example.  The best match wins.
       return request.accept_languages.best_match(['de', 'fr', 'en'])

    @babel.timezoneselector
    def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone
        return None

.. code-block:: python
    :caption: Async Code

    import asyncio
    from quart import g, request

    @babel.localeselector
    async def get_locale():
       # We will use async sleep to give an example that this can
       # be async. Don't do this in production. 
       await asyncio.sleep(0.1)
       # if a user is logged in, use the locale from the user settings
       user = getattr(g, 'user', None)
       if user is not None:
           return user.locale
       # otherwise try to guess the language from the user accept
       # header the browser transmits.  We support de/fr/en in this
       # example.  The best match wins.
       return request.accept_languages.best_match(['de', 'fr', 'en'])

    @babel.timezoneselector
    async def get_timezone():
        # We will use async sleep to give an example that this can
        # be async. Don't do this in production. 
        await asyncio.sleep(0.2)
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone
        return None

.. note::
    The example above assumes that the current user is stored on the
    :data:`Quart.g` object.

Quart Babel also comes with two helper functions that can be used to help determine
the user locale and timezone by the request object. They are :func:`select_locale_by_request`
and :func:`select_timezone_by_request`. This can be used in your locale and timezone selector
function in case no user information is available. This functions are coroutines.

.. code-block:: python

    import asyncio
    from quart import g, request
    from quart_babel import select_locale_by_request, select_timezone_by_request

    @babel.localeselector
    async def get_locale():
       # if a user is logged in, use the locale from the user settings
       user = getattr(g, 'user', None)
       if user is not None:
           return user.locale
       # otherwise try to guess the language from the user accept
       # header the browser transmits.  We support de/fr/en in this
       # example.  The best match wins.
       return await select_locale_by_request()

    @babel.timezoneselector
    async def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone
        return await select_timezone_by_request()