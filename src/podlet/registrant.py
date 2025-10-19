"""Abstract base class for all registrants in the Podlet DI framework."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Generator

from .types import RegistrantIdentity, RegistrantKind


if TYPE_CHECKING:
    from .registry import Registry

class RegistrantAbstract(ABC):
    """Base class for all registrants within the Bootstrap DI system."""

    # == Class Methods =========================================================

    @classmethod
    @abstractmethod
    def kind(cls) -> RegistrantKind:
        """Returns the _kind_ of this registrant as a string. (ex. 'resource', 'service', 'factory','middleware', 'plugin', etc.)"""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def identity(cls) -> str:
        """Returns the identity of this registrant as a string. (ex. 'logging', 'database', 'cache', etc.)"""
        raise NotImplementedError()
    
    @classmethod
    def register_with(cls, registry: Registry) -> None:
        registry.register(cls)

    # == Instance Methods ======================================================


    @abstractmethod
    def initialize(self) -> None:
        """Runs once and is then completely deleted from the instance via the __init__ method to guarantee that contract is enforced."""
        pass
    
    @property
    def options(self) -> Dict[str, Any]:
        """Get the options for this registrant instance."""
        if self.registry is None:
            return {}
        
        return self.registry.get_registrant_options(self.__class__)
        
    # == Protected Methods and Properties ==================================
    
    def __init__(self, registry: Registry) -> None:
        """PRIVATE: Do not call this directly, use the abstract `initialize()` method instead."""
        self.registry = registry
        
        with self._initialization_context():
            # Initialize this instance
            self.initialize()

        # Overwrite initialize method to make it a noop instead of deleting it
        # This ensures the contract is enforced.
        self.initialize = lambda *args, **kwargs: None

    @contextmanager
    def _initialization_context(self) -> Generator[None, None, None]:
        """Context manager to handle both the initialization state and the enforcement of that contract."""
        if self.is_initialized:
            raise RuntimeError(f"{self!r} is already initialized.")
        if self.is_initializing:
            raise RuntimeError(f"{self!r} is already initializing.")
        
        self._is_initializing = True # start 
        try:
            yield 
        finally:
            self._is_initializing = False
            self._is_initialized = True

    @property
    def is_initialized(self) -> bool: 
        return hasattr(self, "_is_initialized") and self._is_initialized

    @property
    def is_initializing(self) -> bool: 
        return hasattr(self, "_is_initializing") and self._is_initializing
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(kind={self.kind()!r}, identity={self.identity()!r})"

    def __str__(self) -> str:
        return self.__repr__()
