.. _cheatsheet:

==========
Cheatsheet
==========

Basic App
---------

.. code-block:: python

    from quart import Quart, render_template
    from quart_babel import Babel, format_gettext

    app = Quart(__name__)

    babel = Babel(app)

    @app.route("/index")
    async def index():
        hello = format_gettext('Hello')

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
        hello = format_gettext('Hello')

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

    BABEL_DEFAULT_LOCALE = 'de_DE'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Berlin'
    BABEL_CONFIGURE_JINJA = True # Showing default as example
    BABEL_DOMAIN = 'myapp'

    app = Quart(__name__)
    app.config.from_pyfile(__name__)

    Babel(app)

    # Setup the rest of the app

Locale & Timezone Selector Functions
------------------------------------

.. code-block:: python
    :caption: Async Code

    import asyncio
    from quart import g, request
    from quart_babel import Babel, select_locale_by_request, select_timezone_by_request
    from quart_babel.typing import ASGIRequest, IPApiKey

    app = Quart(__name__)

    async def locale_selector(request: ASGIRequest):
       # We will use async sleep to give an example that this can
       # be async. Don't do this in production. 
       await asyncio.sleep(0.1)
       # if a user is logged in, use the locale from the user settings
       user = getattr(g, 'user', None)
       if user is not None:
           return user.locale
       # otherwise use the select locale by request function.
       return select_locale_by_request(request)

    async def timezone_selector(request: ASGIRequest, ipapi_key: IPApiKey | None):
        # We will use async sleep to give an example that this can
        # be async. Don't do this in production. 
        await asyncio.sleep(0.2)
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone
        # otherwise use the select timezone by request function.
        return select_timezone_by_request(request, ipapi_key)
    
    babel = Babel(app, locale_selector=get_locale, timezone_selector=timezone_selector)

Formatting Dates & Times
------------------------
The below code assumes that you are within the app context. 

.. code-block:: python 

    orig_date = datetime(1987, 3, 5, 17, 12)

    date = format_date(orig_date)
    date_time = format_datetime(orig_date)
    time = ormat_time(orig_date)

    delta = timedelta(6)
    time_d = format_timedelta(delta, threshold=1)

Formatting Numbers
------------------

The below code assumes that you are within the app context. 

.. code-block:: python 
    
    # Regular number
    number = 1099
    t_num = format_number(number)

    # Decimal number
    dec_number = 1010.99
    d_num = format_decimal(Decimal(dec_number))

    # Percentage number
    per_number = 0.19
    p_num = format_percent(per_number)

    # Scientific number
    sci_number = 10000
    s_num = format_scientific(sci_number)

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
        simple_string = gettext(u'A simple string')

        # String with value
        value_string = gettext(u'Value: %(value)s', value=42)

        # Plural string
        p_string = ngettext(u'%(num)s Apple', u'%(num)s Apples', number_of_apples)

        # .... Additional route code here, such as return. 
    
Lazy Strings
------------

.. code-block:: python

    from quart_babel import lazy_gettext

    class MyForm(formlibrary.FormBase):
        success_message = lazy_gettext(u'The form was successfully saved.')

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
