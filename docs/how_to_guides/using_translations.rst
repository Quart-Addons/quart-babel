.. _using_translations:

==================
Using Translations
==================

The other big part next to date formatting are translations.  For that,
Quart uses :mod:`gettext` together with Babel.  The idea of gettext is
that you can mark certain strings as translatable and a tool will pick all
those up, collect them in a separate file for you to translate.  At
runtime the original strings (which should be English) will be replaced by
the language you selected.

There are two functions responsible for translating: :func:`gettext` and
:func:`ngettext`.  The first to translate singular strings and the second
to translate strings that might become plural.  Here some examples:

.. code-block:: python
    :caption: gettext and ngettext examples

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

Additionally if you want to use constant strings somewhere in your
application and define them outside of a request, you can use a lazy
strings.  Lazy strings will not be evaluated until they are actually used.
To use such a lazy string, use the :func:`lazy_gettext` function:

.. code-block:: python
    :caption: lazy_gettext example

    from quart_babel import lazy_gettext

    class MyForm(formlibrary.FormBase):
        success_message = lazy_gettext(u'The form was successfully saved.')

Translating Applications
------------------------

First you need to mark all the strings you want to translate in your
application with :func:`gettext` or :func:`ngettext`.  After that, it's
time to create a ``.pot`` file.  A ``.pot`` file contains all the strings
and is the template for a ``.po`` file which contains the translated
strings.  Babel can do all that for you.

First of all you have to get into the folder where you have your
application and create a mapping file.  For typical Flask applications, this
is what you want in there:

.. code-block:: ini

    [python: **.py]
    [jinja2: **/templates/**.html]
    extensions=jinja2.ext.autoescape,jinja2.ext.with_

Save it as ``babel.cfg`` or something similar next to your application.
Then it's time to run the `pybabel` command that comes with Babel to
extract your strings:

.. code-block:: console

    $ pybabel extract -F babel.cfg -o messages.pot .

If you are using the :func:`lazy_gettext` function you should tell pybabel
that it should also look for such function calls:

.. code-block:: console

    $ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

This will use the mapping from the ``babel.cfg`` file and store the
generated template in ``messages.pot``.  Now we can create the first
translation.  For example to translate to German use this command::

.. code-block:: console
    
    $ pybabel init -i messages.pot -d translations -l de

``-d translations`` tells pybabel to store the translations in this
folder.  This is where Flask-BabelPlus will look for translations.  Put it
next to your template folder.

Now edit the ``translations/de/LC_MESSAGES/messages.po`` file as needed.
Check out some gettext tutorials if you feel lost.

To compile the translations for use, ``pybabel`` helps again:

.. code-block:: console

    $ pybabel compile -d translations

What if the strings change?  Create a new ``messages.pot`` like above and
then let ``pybabel`` merge the changes:

.. code-block::  console

    $ pybabel update -i messages.pot -d translations

Afterwards some strings might be marked as fuzzy (where it tried to figure
out if a translation matched a changed key).  If you have fuzzy entries,
make sure to check them by hand and remove the fuzzy flag before
compiling.

Quart-Babel looks for message catalogs in ``translations`` directory
which should be located under Quart application directory. Default
domain is "messages".

For example, if you want to have translations for German, Spanish and French,
directory structure should look like this:

    translations/de/LC_MESSAGES/messages.mo
    translations/sp/LC_MESSAGES/messages.mo
    translations/fr/LC_MESSAGES/messages.mo

Translation Domains
-------------------

By default, Quart-Babel will use "messages" domain, which will make it use translations
from the ``messages.mo`` file. It is not very convenient for third-party Quart extensions,
which might want to localize themselves without requiring user to merge their translations
into "messages" domain.

Quart-Babel allows extension developers to specify which translation domain to
use:

.. code-block:: python

    from quart_babel import Domain

    mydomain = Domain(domain='myext')

    mydomain.lazy_gettext('Hello World!')

:class:`Domain` contains all gettext-related methods (:meth:`~Domain.gettext`,
:meth:`~Domain.ngettext`, etc).

In previous example, localizations will be read from the ``myext.mo`` files, but
they have to be located in ``translations`` directory under users Flask application.
If extension is distributed with the localizations, it is possible to specify
their location:

.. code-block:: python

    from quart_babel import Domain

    from quart_myext import translations
    mydomain = Domain(translations.__path__[0])

``mydomain`` will look for translations in extension directory with default (messages)
domain.

It is also possible to change the translation domain used by default,
either for each app or per request.

To set the :class:`Domain` that will be used in an app, pass it to
:class:`Babel` on initialization:

.. code-block:: python

    from quart import Quart
    from quart_babel import Babel, Domain

    app = Quart(__name__)
    domain = Domain(domain='myext')
    babel = Babel(app, default_domain=domain)

Translations will then come from the ``myext.mo`` files by default.

To change the default domain in a request context, call the
:meth:`~Domain.as_default` method from within the request context:

.. code-block:: python

    from quart import Quart
    from quart_babel import Babel, Domain, gettext

    app = Quart(__name__)
    domain = Domain(domain='myext')
    babel = Babel(app)

    @app.route('/path')
    def demopage():
        domain.as_default()

        return gettext('Hello World!')

``Hello World!`` will get translated using the ``myext.mo`` files, but
other requests will use the default ``messages.mo``. Note that a
:class:`Babel` must be initialized for the app for translations to
work at all.
