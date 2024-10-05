.. _translating:

========================
Translating Applications
========================

First you need to mark all the strings you want to translate in your
application with :func:`gettext` or :func:`ngettext`.  After that, it's
time to create a ``.pot`` file.  A ``.pot`` file contains all the strings
and is the template for a ``.po`` file which contains the translated
strings.  Babel can do all that for you.

First of all you have to create a mapping file. For typical Quart applications,
this is what you want in there:

.. sourcecode:: ini

    [python: **.py]
    [jinja2: **/templates/**.html]

Save it as ``babel.cfg`` or something similar next to your application.
Then it's time to run the `pybabel` command that comes with Babel to
extract your strings::

    $ pybabel extract -F babel.cfg -o messages.pot .

If you are using the :func:`lazy_gettext` function you should tell pybabel
that it should also look for such function calls::

    $ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

This will use the mapping from the ``babel.cfg`` file and store the
generated template in ``messages.pot``.  Now we can create the first
translation.  For example to translate to German use this command::

    $ pybabel init -i messages.pot -d translations -l de

``-d translations`` tells pybabel to store the translations in a directory
called "translations".  This is the default folder where Flask-Babel will look
for translations unless you changed `BABEL_TRANSLATION_DIRECTORIES` and should
be at the root of your application.

Now edit the ``translations/de/LC_MESSAGES/messages.po`` file as needed.
Check out some gettext tutorials if you feel lost.

To compile the translations for use, ``pybabel`` helps again::

    $ pybabel compile -d translations

What if the strings change?  Create a new ``messages.pot`` like above and
then let ``pybabel`` merge the changes::

    $ pybabel update -i messages.pot -d translations

Afterwards some strings might be marked as fuzzy (where it tried to figure
out if a translation matched a changed key).  If you have fuzzy entries,
make sure to check them by hand and remove the fuzzy flag before
compiling.
