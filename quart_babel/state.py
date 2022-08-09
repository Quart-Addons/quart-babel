"""
quart_babel.state

Dataclass for the babel state. This file
is need to eliminate circular imports.
"""
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from quart import Quart

if TYPE_CHECKING:
    from .core import Babel
    from .domain import Domain

@dataclass
class _BabelState:
    """
    Class for holding the state for Babel.
    """
    babel: Babel
    app: Quart
    domain: Domain
    locale_cache: dict = field(init=False, repr=False)

    def __repr__(self) -> str:
        return f'<_BabelState({self.babel}, {self.app}, {self.domain})>'
