"""Helper functions and utilities for the Podlet DI framework."""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Any

from .types import RegistrantIdentity, RegistrantKind


def snake_case(word: str) -> str:
    """Convert a given string to snake_case.
    
    Credit: `inflection` package
    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
    word = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', word)
    word = word.replace("-", "_")
    return word.lower()


def only_while_initializing(func):
    """Decorator to ensure that a method of a registrant is only called while initializing."""
    def wrapper(self, *args, **kwargs):
        # Import here to avoid circular imports
        from .registrant import RegistrantAbstract
        from .resource import wraps
        
        if not isinstance(self, RegistrantAbstract):
            raise TypeError(f"Decorator only_while_initializing(): The {self.__class__.__name__} does not inherit from RegistrantAbstract, which is a requirement of this decorator.")
        if not self._is_initializing:
            raise RuntimeError(f"Contract violation attempted detected: {self!r}.{func.__name__}() can not be called outside of initialization.")
        return func(self, *args, **kwargs)
    return wrapper


@dataclass(init=False)
class Resolve:
    unknown: Any
    
    def __init__(self, unknown: Any) -> None:
        self.unknown = unknown
    
    @property
    def is_registrant(self) -> bool:
        # Import here to avoid circular imports
        from .registrant import RegistrantAbstract
        
        if isinstance(self.unknown, RegistrantAbstract): return True
        if isinstance(self.unknown, type) and issubclass(self.unknown, RegistrantAbstract): return True
        return False
    
    @property
    def is_str(self) -> bool:
        if isinstance(self.unknown, str): return True
        return False
    
    @property
    def is_registry(self) -> bool:
        # Import here to avoid circular imports
        from .registry import Registry
        
        if isinstance(self.unknown, Registry): return True
        if isinstance(self.unknown, type) and issubclass(self.unknown, Registry): return True
        return False
    
    
    @property
    def kind(self) -> str:
        if self.is_str: return str(self.unknown)
        if self.is_registrant: return self.unknown.kind()
        if self.is_registry: return self.unknown.kind()
        raise TypeError(f"Cannot resolve kind from {self.unknown!r}")    
    
    @property
    def identity(self) -> str:
        if self.is_str: return str(self.unknown)
        if self.is_registrant: return self.unknown.identity()
        raise TypeError(f"Cannot resolve identity from {self.unknown!r}")
