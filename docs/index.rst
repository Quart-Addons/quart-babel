:orphan:

.. title:: Quart Babel Documentation

.. image:: _static/logo.png
   :width: 300px
   :alt: Quart Babel Logo
   :align: right

Quart Babel
-------------

Quart-Babel is an extension to `Quart` that adds i18n and i10n support to any
`Quart` application with the help of `babel`_, `pytz`_, and `speaklater`_. It 
has builtin support for date formatting with timezone support as weel as a very
simple and friendly interface :mod:`gettext` translations.

This is a fork of `Flask-BabelPlus`, which has been ported over to `Quart` with
async features added. `Flask-BabelPlus` is a fork of the offical `Flask-Babel`
extension. 

Quart-Babel comes with the following features:

1. It is possible to use multiple language catalogs in one Flask application;
2. Localization domains: your extension can package localization file(s) and
   use them if necessary;
3. Does not reload localizations for each request.

You can also pass the localization `Domain` in the extension initilazation process. 


Quart-Babel is developed on github, `here <https://github.com/Quart-Addons/quart-uploads>`_ . 

For more information on Quart, `visit here <https://quart.palletsprojects.com/en/latest/>`_ .

Links
-----
* [Flask-BabelPlus](https://github.com/sh4nks/flask-babelplus)
* [Flask-BabelEx](https://github.com/mrjoes/flask-babelex)
* [Original Flask-Babel Extension](https://github.com/python-babel/Flask-Babel)

Tutorials
---------

.. toctree::
   :maxdepth: 2

   tutorials/index.rst

How to guides
-------------

.. toctree::
   :maxdepth: 2

   how_to_guides/index.rst

Reference
---------

.. toctree::
   :maxdepth: 2

   references/index.rst

.. _babel: http://babel.edgewall.org/
.. _pytz: http://pytz.sourceforge.net/
.. _speaklater: https://github.com/sh4nks/flask-babelplus/blob/master/flask_babelplus/speaklater.py
