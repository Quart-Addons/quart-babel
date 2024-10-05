.. _configuration:

=============
Configuration  
=============

To get started all you need to do is to instanciate a :class:`Babel`
object after configuring the application::

.. code-block:: python

  from quart import Quart
  from quart_babel import Babel

  app = Quart(__name__)
  babel = Babel(app)

You can also use the factory method of initializing extensions:

.. code-block:: python

  babel.init_app(app)

To disable jinja support, include ``configure_jinja=False`` in the Babel
constructor call. The babel object itself can be used to configure the babel
support further. Babel has the following configuration values that can be used
to change some internal defaults:

.. list-table:: Configuration Variables
    :widths: auto 
    :header-rows: 1

    * - Variable
      - Type
      - Default
      - Description
    * - `BABEL_DEFAULT_LOCALE`
      - ``str``
      - ``'en_US'``
      - The default locale to use if no locale selector is registered.
    * - `BABEL_DEFAULT_TIMEZONE`
      - ``str``
      - ``'UTC'``
      - The timezone to use for user facing dates.
    * - `BABEL_DOMAIN`
      - ``str | list[str]``
      - ``"messages"``
      - The default translation domain(s).
    * - `BABEL_TRANSLATION_DIRECTORIES`
      - ``str | list[str]``
      - ``"translations"``
      - The directories where translations can be found.

For more complex applications you might want to have multiple applications
for different users which is where selector functions come in handy. The
first time the babel extension needs the locale (locale code/ID) of the
current user it will call a :meth:`~Babel.localeselector` function, and
the first time the timezone is needed it will call a
:meth:`~Babel.timezoneselector` function.

If any of these methods return `None` the extension will automatically
fall back to what's in the config.  Furthermore for efficiency that
function is called only once and the return value then cached.  If you
need to switch the language between a request, you can :func:`refresh` the
cache.


Example selector functions::

.. code-block:: python
    from quart import Quart, g, request

    def get_locale():
        # if a user is logged in, use the locale from the user settings
        user = getattr(g, 'user', None)
        if user is not None:
            return user.locale
        # otherwise try to guess the language from the user accept
        # header the browser transmits.  We support de/fr/en in this
        # example.  The best match wins.
        return request.accept_languages.best_match(['de', 'fr', 'en'])

    def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone

    app = Quart(__name__)
    babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)

The example above assumes that the current user is stored on the
:data:`quart.g` object.
