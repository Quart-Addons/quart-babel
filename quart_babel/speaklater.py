"""
quart_babel.speaklater

Provides LazyString class for Quart-Babel.
"""

class LazyString(object):
    """
    The `LazyString` class provides the ability to declare
    translations without app context. The translations don't
    happen until they are actually needed.
    """
    def __init__(self, func: callable, *args, **kwargs):
        """
        Constract a Lazy String.

        Arguments:
            func: The function to use for the string.
            args: Arguments for the function.
            kwargs: Kwargs for the function.
        """
        self._func = func
        self._args = args
        self._kwargs = kwargs

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
        return str(self._func(*self._args, **self._kwargs))

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
