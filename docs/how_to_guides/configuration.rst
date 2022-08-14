.. _configuration:

=============
Configuration  
=============

To get started all you need to do is to instanciate a :class:`Babel`
object after configuring the application::

.. code-block:: python

    from quart import Quart
    from quart-babel import Babel

    app = Quart(__name__)
    app.config.from_pyfile('mysettings.cfg')
    babel = Babel(app)

You can also use the factory method of initializing extensions:

.. code-block:: python

    babel.init_app(app)

The Babel object iteself can be used to to change some internal defaults.

.. list-table:: Configuration Variables
    :widths: auto 
    :header-rows: 1

    * - Variable
      - Type
      - Default
      - Description
    * - `BABEL_DEFAULT_LOCALE`
      - ``str``
      - ``'en'``
      - The default locale to use if no locale selector is registered.
    * - `BABEL_DEFAULT_TIMEZONE`
      - ``str``
      - ``'UTC'``
      - The timezone to use for user facing dates.
    * - `BABEL_CONFIGURE_JINJA`
      - `bool`
      - ``True``
      - If set to ``True`` some convenient jinja2 filters are added.
    * - `BABEL_DOMAIN`
      - `Domain`
      - ``None``
      - The default translation domain.
    * - `BABEL_IPAPI_KEY`
      - ``str``
      - ``None``
      - The IP API key to use, which is used for `select_timezone_by request`.


