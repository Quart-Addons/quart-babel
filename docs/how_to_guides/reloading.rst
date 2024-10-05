.. _reloading:

=======================
Reloading Translations
=======================

The compiled translations will only be loaded initially. This means you have
to restart the server whenever you compile translations and want to see
those changes. To automatically reload translations you can tell the reloader
to watch the compiled ``.mo`` files::

    $ quart run --extra-files app/translations/en_GB/LC_MESSAGES/messages.mo
    # or
    $ export QUART_RUN_EXTRA_FILES=app/translations/en_GB/LC_MESSAGES/messages.mo
    $ quart run

See `reloader`_ for more details.

.. _reloader: https://flask.palletsprojects.com/en/3.0.x/cli/#watch-and-ignore-files-with-the-reloader