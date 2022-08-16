.. _cheatsheet:

==========
Cheatsheet
==========

Basic App
---------

.. code-block:: python

    from quart import Quart, render_template
    from quart_uploads import Babel, format_gettext

    app = Quart(__name__)

    babel = Babel(app)

    @app.route("/index")
    async def index():
        hello = await format_gettext('Hello')

        return await render_template('index.html', hello=hello)

Large Applications
------------------

.. code-block:: python
    :caption: yourapplication/routes.py

    from quart import Blueprint 
    from quart_babel import format_gettext

    bp = Blueprint('main', __name__, url_prefix='/photos')

    @app.route("/index")
    async def index():
        hello = await format_gettext('Hello')

        return await render_template('index.html', hello=hello)

    # Routes & additional code here. 

.. code-block:: python
    :caption: youapplication/app.py

    from quart import Quart
    from quart_babel import Babel

    babel = Babel()

    def create_app() -> Quart:
        app = Quart(__name__)

        babel.init_app(app)

        from .routes import bp as main_bp
        app.register_blueprint(main_bp)

        # Other app registration here. 
        
        return app

Configuration Variables
-----------------------

.. code-block:: python
    :caption: app.py 

    from quart import Quart
    from quart_babel import Babel

    BABEL_DEFAULT_LOCALE = 'de'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Berlin'
    BABEL_CONFIGURE_JINJA = True # Showing default as example
    BABEL_DOMAIN = 'myapp'

    app = Quart(__name__)
    app.config.from_pyfile(__name__)

    Babel(app)

    # Setup the rest of the app

Locale & Timezone Selector Functions
------------------------------------

The locale selector function can be sync or async. 

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

Locale & Timezone Helper Functions
----------------------------------

Quart-Babel comes with two helper functions to help you determine the
users locale and timezone. They are `select_locale_by_request` and 
`select_timezone_by_request`. These two functions are intended to be
used with your locale and timezone selector functions. 

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

.. note::

    When using these two helper functions make sure that your locale selector
    and timezone selector functions are coroutines. 

Formatting Dates & Times
------------------------
The below code assumes that you are within the app context. 

.. code-block:: python 

    orig_date = datetime(1987, 3, 5, 17, 12)

    date = await format_date(orig_date)
    date_time = await format_datetime(orig_date)
    time = await format_time(orig_date)

    delta = timedelta(6)
    time_d = await format_timedelta(delta, threshold=1)

Formatting Numbers
------------------

The below code assumes that you are within the app context. 

.. code-block:: python 
    
    # Regular number
    number = 1099
    t_num = await format_number(number)

    # Decimal number
    dec_number = 1010.99
    d_num = await format_decimal(Decimal(dec_number))

    # Percentage number
    per_number = 0.19
    p_num = await format_percent(per_number)

    # Scientific number
    sci_number = 10000
    s_num = await format_scientific(sci_number)

Using Translations
------------------

.. code-block:: python

    from datetime import datetime
    from quart import quart
    from quart_babel import Babel, gettext, ngettext

    app = Quart(__name__)
    Babel(app)

    @app.route('/')
    async def index():
        # Simple string 
        simple_string = await gettext(u'A simple string')

        # String with value
        value_string = await gettext(u'Value: %(value)s', value=42)

        # Plural string
        p_string = await ngettext(u'%(num)s Apple', u'%(num)s Apples', number_of_apples)

        # .... Additional route code here, such as return. 
    
Lazy Strings
------------

.. code-block:: python

    from quart_babel import lazy_gettext

    class MyForm(formlibrary.FormBase):
        success_message = lazy_gettext(u'The form was successfully saved.')

Lazy Strings are awaitable and need to be called like such:

.. code-block:: python

    await success_message

Translation Domains
-------------------

.. code-block:: python
    :caption: Application Custom Domain

    from quart import Quart
    from quart_babel import Babel, Domain

    app = Quart(__name__)
    domain = Domain(domain='myext')
    babel = Babel(app, default_domain=domain)

.. code-block:: python
    :caption: Extension Custom Domain 

    from quart_babel import Domain

    mydomain = Domain(domain='myext')

    mydomain.lazy_gettext('Hello World!')
