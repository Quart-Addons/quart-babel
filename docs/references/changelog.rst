.. _changelog:

---------
Changelog
---------

Version 1.0.1 - 2/4/23
----------------------
Updated dependecies due to sphinx documentation generation failure. Due to this we had to 
revert back to using ipapi library over aioipapi. 

Version 1.0.0 - 2/3/23
-----------------------
In this release of Quart Babel the way the locale and timezone information is obtained
from a user was changed to ASGI middleware. Note that this will provide breaking changes
to the last version. The following was changed:

* Changed to use ASGI middleware over using Quarts request object in order to allow Quart
  Babel to work with other Quart extensions like WTF for example.

* Changed gettext and format (date and number) functions from async to sync. Async functions
  are no longer needed since all locale and timezone detection is done with middleware and saved
  to context vars. This includes custom detect functions as well.

* Changed how to declare custom locale and timezone detection functions. Decorators are no longer
  used.

* Updated typing for all classes and functions. 

* Updated doc strings for all classes and functions. 

* Updated documentation to reflect changes noted above. 

* Added changelog to documentation. 

* Added development page to documentation.

* Changed versioning format to `Semantic Versioning <https://semver.org/>`_. 

Version 0.0.3 - 8/16/22
-----------------------

First initial release of Quart Babel. Made the extension work like Flask-BabelPlus.