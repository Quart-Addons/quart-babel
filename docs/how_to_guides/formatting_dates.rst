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

To play with the date formatting from the console, you can use the
:meth:`~quart.Quart.test_request_context` method:

>>> app.test_request_context().push()

Here some examples:

>>> from quart_babel import format_datetime
>>> from datetime import datetime
>>> format_datetime(datetime(1987, 3, 5, 17, 12))
u'Mar 5, 1987 5:12:00 PM'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'full')
u'Thursday, March 5, 1987 5:12:00 PM World (GMT) Time'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'short')
u'3/5/87 5:12 PM'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'dd mm yyy')
u'05 12 1987'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'dd mm yyyy')
u'05 12 1987'

And again with a different language:

>>> app.config['BABEL_DEFAULT_LOCALE'] = 'de'
>>> from quart_babel import refresh; refresh()
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'EEEE, d. MMMM yyyy H:mm')
u'Donnerstag, 5. M\xe4rz 1987 17:12'

For more format examples head over to the `babel <https://babel.pocoo.org/en/latest/>`_ documentation.