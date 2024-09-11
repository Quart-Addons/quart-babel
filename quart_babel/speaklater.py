"""
quart_babel.speaklater
"""
import typing as t


class LazyString(object):
    """
    The `LazyString` class provides the ability to declare
    translations without app context. The translations don't
    happen until they are actually needed.
    """
    def __init__(
            self,
            func: t.Callable,
            *args: t.Any,
            **kwargs: t.Any
    ) -> None:
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

    def __getattr__(self, attr: t.Any) -> str:
        if attr == "__setstate__":
            raise AttributeError(attr)
        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)
        raise AttributeError(attr)

    def __repr__(self) -> str:
        return f"l'{str(self)}'"

    def __str__(self) -> str:
        return str(self._func(*self._args, **self._kwargs))

    def __len__(self) -> int:
        return len(str(self))

    def __getitem__(self, key: t.Any) -> str:
        return str(self)[key]

    def __iter__(self) -> t.Iterator[str]:
        return iter(str(self))

    def __contains__(self, item: str) -> bool:
        return item in str(self)

    def __add__(self, other: str) -> str:
        return str(self) + other

    def __radd__(self, other: str) -> str:
        return other + str(self)

    def __mul__(self, other: t.Any) -> str:
        return str(self) * other

    def __rmul__(self, other: t.Any) -> str:
        return other * str(self)

    def __lt__(self, other: str) -> bool:
        return str(self) < other

    def __le__(self, other: str) -> bool:
        return str(self) <= other

    def __eq__(self, other: t.Any) -> bool:
        return str(self) == other

    def __ne__(self, other: t.Any) -> bool:
        return str(self) != other

    def __gt__(self, other: str) -> bool:
        return str(self) > other

    def __ge__(self, other: str) -> bool:
        return str(self) >= other

    def __html__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __mod__(self, other: str) -> str:
        return str(self) % other

    def __rmod__(self, other: str) -> str:
        return other + str(self)
