"""Central registrar for managing multiple registries in the Podlet DI framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Self, Type, TypeVar, cast, overload

from .helpers import Resolve
from .registry import Registry
from .types import RegistrantIdentity, RegistrantKind, Tr


@dataclass
class Registrar:
    """Registrar manages registries that themselves manage a specific _kind_ (not type) of RegistrantAbstract.
    
    Manages registration, initialization, and retrieval of RegistrantAbstract subclasses.
    
    Notes:
        - Not a Generic class, ABC, or Protocol.
        - Part of the larger Bootstrap DI system.
        - Use standalone, or as a base class for a Bootstrap class.    
        
    Options:
        structure: Dict[str, Any]
            A dictionary of nested options
            {
                REGISTRY.kind(): {
                    REGISTRANT.identity(): {    
                        OPTION_KEY: OPTION_VALUE
                    }
                }
            }    
    """
    
    registries: Dict[str, Registry[Any]] = field(default_factory=dict)
    options:    Dict[str, Any]           = field(default_factory=dict)
    
    def get_registry_options(self, kind_or_type: str | Type[Any]) -> Dict[str, Any]:
        """Get the options for a specific registry by its kind or type."""
        kind = Resolve(kind_or_type).kind
        if kind in self.options:
            return cast(Dict[str, Any], self.options[kind])
        return {}
    
    def set_registry_options(self, kind_or_type: str | Type[Any], options: Dict[str, Any]) -> None:
        """Set the options for a specific registry by its kind or type."""
        kind = Resolve(kind_or_type).kind
        self.options[kind] = options

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set the options for the entire registrar.
        
        {
            REGISTRY.kind(): {
                REGISTRANT.identity(): {    
                    OPTION_KEY: OPTION_VALUE
                }
            },
            ...
        }
        """
        self.options = options

    @overload
    def has_registry(self, kind_or_type: str) -> bool: ...
    @overload
    def has_registry(self, kind_or_type: Type[Any]) -> bool: ...

    def has_registry(self, kind_or_type: str | Type[Any]) -> bool:
        return Resolve(kind_or_type).kind in self.registries

    @overload
    def get_registry(self, kind_or_type: str) -> Registry[Any]: ...
    @overload
    def get_registry(self, kind_or_type: Type[Tr]) -> Registry[Tr]: ...

    def get_registry(self, kind_or_type: str | Type[Tr]) -> Registry[Tr] | Registry[Any]:
        """Get a Registry instance for a specific kind of registrant."""
        kind = Resolve(kind_or_type).kind
        if kind not in self.registries:
            raise KeyError(f"No registry found for kind '{kind}'")
        registry = self.registries[kind]
        
        if not isinstance(registry, str):
            registry = cast(Registry[Tr], registry)
        
        return registry
     
    def register_registry(self, registry_klass: Type[Registry[Any]]) -> None:
        """Register a typed Registry class with this registrar."""
        if not issubclass(registry_klass, Registry):
            raise TypeError(f"Cannot register {registry_klass}: must be a subclass of Registry")

        kind = Resolve(registry_klass).kind
        if kind != registry_klass.kind():
             raise ValueError(f"Cannot register {registry_klass.__name__}: its kind ('{kind}') does not match the registry's kind ('{registry_klass.kind()}')")

        if kind not in self.registries:
            self.registries[kind] = registry_klass(registrar=self)
            
        return self.registries[kind]

    
    
    def register(self, *klasses: Type[Any]) -> None:
        """Register multiple RegistrantAbstract classes with a Registry that has been setup via register_registry()."""
        for klass in klasses:
            kind = Resolve(klass).kind

            # Initialize Registry (if needed)
            if not self.has_registry(kind):
                raise ValueError(f"Cannot register {klass.__name__}: as no registry exists for kind '{kind}' -- use register_registry() ensure it's ready to accept RegistrantAbstracts of this kind.")

            # Get the registry and register the class
            registry = self.get_registry(kind)
            registry.register(klass)
        
        
        
    @overload
    def get(self, kind_or_type: RegistrantKind, ident_or_type: RegistrantIdentity) -> Any: ...
    @overload
    def get(self, kind_or_type: RegistrantKind, ident_or_type: Type[Any]) -> Any: ...
    @overload
    def get(self, kind_or_type: Type[Tr], ident_or_type: RegistrantIdentity) -> Tr: ...
    @overload
    def get(self, kind_or_type: Type[Tr], ident_or_type: Type[Tr]) -> Tr: ...

    def get(self, kind_or_type: RegistrantKind | Type[Tr], ident_or_type: RegistrantIdentity | Type[Tr]) -> Any | Tr:
        """Get a registrant instance by its kind and identity or type."""
        registry = self.get_registry(kind_or_type)
        return registry.get(ident_or_type)
