.. _formatting_numbers:

==================
Formatting Numbers
==================

To format numbers you can use the :func:`format_number`,
:func:`format_decimal`, :func:`format_currency`, :func:`format_percent` and :func:`format_scientific`
functions.

To play with the date formatting from the console, you can use the
:meth:`~quart.Quart.test_request_context` method:

>>> app.test_request_context().push()

Here are some examples:

>>> from quart_babel import format_number
>>> format_number(1099)
'1,099'

>>> from quart_babel import format_decimal
>>> format_decimal(1.2346)
u'1.235'

>>> from quart_babel import format_currency
>>> format_currency(1099.98, 'USD')
'$1,099.98'

>>> from quart_babel import format_percent
>>> format_percent(0.34)
'34%'

>>> from quart_babel import format_scientific
>>> format_scientific(10000)
'1E4'

And again with a different language:

>>> app.config['BABEL_DEFAULT_LOCALE'] = 'de'
>>> from quart_babel import refresh; refresh()

>>> format_number(1099)
'1.099'

>>> format_decimal(1.2346)
'1,235'

>>> format_currency(1099.98, 'USD')
'1.099,98\xa0$'

>>> format_percent(0.34)
'34\xa0%'

>>> format_scientific(10000)
'1E4'

For more format examples head over to the `babel <https://babel.pocoo.org/en/latest/>`_ documentation.