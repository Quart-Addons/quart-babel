"""
    speaklater
    ~~~~~~~~~~
    Copied over from Flask-Babel which copied it from 'speaklater'
    and included some fixes. Added the ability to be async.
    See:
      - https://github.com/python-babel/flask-babel/blob/master/flask_babel/speaklater.py
      - https://github.com/mitsuhiko/speaklater/blob/master/speaklater.py
    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations
from typing import Optional

class LazyString(object):
    """
    The `LazyString` class provides the ability to declare
    translations without app context. The translations don't
    happen until they are actually needed.
    """
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self.text: Optional[str] = None

    async def _get_string(self):
        """
        Calls the `Babel` text function in an
        async manner and returns.
        """
        self.text = await self._func(*self._args, **self._kwargs)
        return self

    def __await__(self):
        """
        Provides the ability to call the `Lazy String` using
        await.
        """
        return self._get_string().__await__()

    def __getattr__(self, attr):
        if attr == "__setstate__":
            raise AttributeError(attr)
        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)
        raise AttributeError(attr)

    def __repr__(self):
        return f"l'{str(self)}'"

    def __str__(self):
        return str(self.text)

    def __len__(self):
        return len(str(self))

    def __getitem__(self, key):
        return str(self)[key]

    def __iter__(self):
        return iter(str(self))

    def __contains__(self, item):
        return item in str(self)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    def __mul__(self, other):
        return str(self) * other

    def __rmul__(self, other):
        return other * str(self)

    def __lt__(self, other):
        return str(self) < other

    def __le__(self, other):
        return str(self) <= other

    def __eq__(self, other):
        return str(self) == other

    def __ne__(self, other):
        return str(self) != other

    def __gt__(self, other):
        return str(self) > other

    def __ge__(self, other):
        return str(self) >= other

    def __html__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __mod__(self, other):
        return str(self) % other

    def __rmod__(self, other):
        return other + str(self)
