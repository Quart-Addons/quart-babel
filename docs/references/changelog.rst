.. _changelog:

---------
Changelog
---------

Version 1.0.7 - 10/05/24
------------------------

Added py.typed file, which was forgot in version
1.0.6. release.

Version 1.0.6 - 10/05/24
------------------------

The following was changed during this release:

* Made the extension a copy of flask_babel (BREAKING CHANGE)
* Removed middleware no longer needed. 
* Updated dependencies, since some are no longer needed, since middleware is not used.
* Updated documentation to match changes for this release. 
* Updated tests to match changes for this release. 

Version 1.0.5 - 09/11/24
-------------------------

The following was changed during this release:

General:

* General file cleanup and formatting. 
* Changed requirements.txt for the docs. 

pyproject.toml file:

* Updated version. 
* Updated dependencies.

Version 1.0.4 - 11/23/23
------------------------

The following was changed during this release:

General:

* Tested extension using Python 3.12.
* Extension now supports Python 3.11 and 3.12.

Dev Container:

* devcontainer.json: Changed name, vscode extensions, and postCreateCommand. postCreateCommand doesn't use shell script anymore.
* Dockerfile: Updated docker version to be 3.12 and removed unused commands.
* Removed postCreateCommand.sh file, since no longer needed.

pyproject.toml file:

* Changed version number to match this release.
* Added Python 3.11 and 3.12 to classifiers.
* Updated Python version to be >= 3.8.
* Updated Quart version to match latest release.
* Added tool.black
* Added tool.isort
* Added tool.mypy


Version 1.0.3 - 10/27/23
------------------------

The release offers minor changes to Quart Babel.

* Quart Version must be >0.18. Past release wouldn't allow 0.19 versions of Quart.

* Changed version in "pyproject.toml" file to match this release.

* Added homepage to "pyproject.toml" file.


Version 1.0.2 - 5/1/23
----------------------
In this release of Quart Babel the following has changed:

* Updated ASGI Tools to latest version and passed receive and 
  send to the request object along with scope. 

* Removed ipapi dependency and the select_timezone_by_request. 
  We hope to bring this feature back in a future release.

* Updated tests.

* Updated docs to reflect changes noted above.

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