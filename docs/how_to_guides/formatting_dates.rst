.. _formatting_dates:

================
Formatting Dates
================

To format dates you can use the :func:`format_datetime`,
:func:`format_date`, :func:`format_time` and :func:`format_timedelta`
functions.  They all accept a :class:`datetime.datetime` (or
:class:`datetime.date`, :class:`datetime.time` and
:class:`datetime.timedelta`) object as first parameter and then optionally
a format string.  The application should use naive datetime objects
internally that use UTC as timezone.  On formatting it will automatically
convert into the user's timezone in case it differs from UTC.

Here some examples:

.. code-block:: python
    :caption: Basic examples

    from datetime import datetime
    from quart import quart
    from quart_babel import Babel, refresh, format_datetime

    app = Quart(__name__)
    Babel(app)

    @app.route('/')
    async def index():
        date_1 = await format_datetime(datetime(1987, 3, 5, 17, 12))
        # date_1 = 'Mar 5, 1987 5:12:00 PM'

        date_2 = await format_datetime(datetime(1987, 3, 5, 17, 12), 'full')
        # date_2 = 'Thursday, March 5, 1987 5:12:00 PM World (GMT) Time'

        date_3 = await format_datetime(datetime(1987, 3, 5, 17, 12), 'short')
        # date_3 = '3/5/87 5:12 PM'

        date_4 = await format_datetime(datetime(1987, 3, 5, 17, 12), 'dd mm yyy')
        # date_4 = '05 12 1987'

        date_5 = await format_datetime(datetime(1987, 3, 5, 17, 12), 'dd mm yyyy')
        # date_5 = '05 12 1987'

        # .... Additional route code here, such as return. 

.. code-block:: python
    :caption: Again with a different language

    # Assume same app as the basic example. 

    @app.route('/de')
    async def de_lang():
        app.config['BABEL_DEFAULT_LOCALE'] = 'de'

        # refresh babel 
        refresh()

        date = await format_datetime(datetime(1987, 3, 5, 17, 12), 'EEEE, d. MMMM yyyy H:mm')
        # date = 'Donnerstag, 5. M\xe4rz 1987 17:12'

        # .... Additional route code here, such as return. 

For more format examples head over to the `babel <https://babel.pocoo.org/en/latest/>`_ documentation.