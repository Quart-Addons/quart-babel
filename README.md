# Quart Babel

![Quart Uploads Logo](logos/logo.png)

Implements i18n and l10n support for Quart.  This is based on the Python
[babel][] module as well as [pytz][] both of which are installed automatically
for you if you install this library.

The original code for this extension was taken from Flask-Babel and Flask-BabelPlus. 
Flask-Babel can be found [here][flask-babel] and Flask-BabelPlus can be found 
[here][flask-babelplus]

# Installation 

Install the extension with the following command:

    $ pip3 install quart-babel

# Usage

To use the extension simply import the class wrapper and pass the Quart app 
object back to here. Do so like this:

    from quart import Quart
    from quart_babel import Babel 

    app = Quart(__name__)
    babel = Babel(app)


# Documentation

The for Quart-Babel and is available [here][docs].

[babel]: https://github.com/python-babel/babel
[pytz]: https://pypi.python.org/pypi/pytz/
[flask-babel]: https://flask-babel.tkte.ch/
[flask-babelplus]: https://github.com/sh4nks/flask-babelplus
[docs]: https://quart-babel.readthedocs.io
