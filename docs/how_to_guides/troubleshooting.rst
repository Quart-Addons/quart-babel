.. _troubleshooting:

===============
Troubleshooting
===============

On Snow Leopard pybabel will most likely fail with an exception.  If this
happens, check if this command outputs UTF-8:

.. code-block:: console
    
    $ echo $LC_CTYPE
    UTF-8

This is a OS X bug unfortunately.  To fix it, put the following lines into
your ``~/.profile`` file:

.. code-block:: console

    export LC_CTYPE=en_US.utf-8

Then restart your terminal.