.. _installation:

============
Installation
============

Quart-Babel is only compatible with Python 3.7 or higher, since this is 
what Quart supports. It can be installed using pip or your favorite python 
package manager.

.. code-block:: console

    pip install quart-babel

.. note::
    If you do not have Python 3.7 or better an error message ``Python 3.7
    is the minimum required version`` will be displayed.

Dependencies
------------

Quart Babel depends on the following packages, which will automatically
be installed with the extension.

- `Quart <https://quart.palletsprojects.com>`_
- `Babel <https://babel.pocoo.org/en/latest/>`_
- `ipapi <https://github.com/ipapi-co/ipapi-python>`_
- `nest_asyncio <https://github.com/erdewit/nest_asyncio>`_

.. warning:: 

    The `nest_asyncio` is a patch to allow nested event loops and this needed in 
    order to get the `gettext` functions available in the template, since they are
    coroutines. The author doesn't know how this effects the performance of `Quart`,
    but it did work in our tests of this extension. If you are already using this in
    your application. We have provided a configuration variable to disable it. this
    variable doesn't need to be set at all, since it defaults to true. See the :ref:`configuration`
    for more information. 