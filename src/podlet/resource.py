from __future__ import annotations

from abc import ABC, abstractmethod
from collections import UserDict
from typing import Any, Dict, Self, Type, TypeVar

from .helpers import only_while_initializing as _only_while_initializing
from .helpers import snake_case
from .registrant import RegistrantAbstract, RegistrantIdentity, RegistrantKind
from .registry import Registry


# Alias, allowing propagation and cohesion when using this module.
only_while_initializing = _only_while_initializing    


class ResourceAbstract(RegistrantAbstract, ABC):
    """Base class for all resources within the Bootstrap DI system."""

    @classmethod
    def kind(cls) -> RegistrantKind:
        return "resource" 
    
    @classmethod
    def identity(cls) -> RegistrantIdentity:
        """Derive identity from class name by converting to snake_case and stripping kind suffix."""
        kind_suffix = f"_{cls.kind()}"
        class_name_snake = snake_case(cls.__name__)
        if class_name_snake.endswith(kind_suffix):
             return class_name_snake[:-len(kind_suffix)]
        return class_name_snake
    

    @abstractmethod # explicit propagation of abstractmethod
    def initialize(self) -> Self:
        """Initialize the resource. This is called by the associated Registry[self.__class__]."""
        return self


    def options(self) -> Dict[str, Any]:
        """Get the ResourceOptions for this resource instance."""
        return self.registry.get_registrant_options(self.identity())
        


class ResourceRegistry(Registry[ResourceAbstract], ABC):
    """A registry specifically for ResourceAbstract subclasses."""
    
    @classmethod
    def kind(cls) -> str: 
        return ResourceAbstract.kind()
