"""Typed registry for managing registrants in the Podlet DI framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Self, Type, TypeVar, cast, get_args, get_origin

from .helpers import Resolve
from .types import RegistrantKind, Tr


if TYPE_CHECKING:
    from .registrant import RegistrantAbstract
    from .registrar import Registrar


@dataclass(init=False)
class Registry(Generic[Tr]):
    """A registry specifically for a RegistrantKind of RegistrantAbstract."""
    

    registered:  Dict[str, Type] = field(default_factory=dict, init=False, repr=False)
    initialized: Dict[str, Tr]   = field(default_factory=dict, init=False, repr=False)

    registrar:   Optional[Registrar]   

            
    @classmethod
    def kind(cls) -> RegistrantKind:
        """Inferred kind of the registry."""
        if not issubclass(cls, Registry): raise TypeError("Can't be called from a non-subclass of Registry.")
        
        # Memoize for this subclass
        if not hasattr(cls, "_kind"): setattr(cls, "_kind", cls._registrant_type().kind())
        return getattr(cls, "_kind")
            
    def __init__(self, registrar: Optional[Any] = None) -> None:
        self.registrar = registrar
        self.registered = {}
        self.initialized = {}
        
                    
            
    # == Helpers ==========================================================
    
    def has_registered(self, ident_or_type: str | Type[Tr]) -> bool:
        return Resolve(ident_or_type).identity in self.registered.keys()

    
    def has_initialized(self, ident_or_type: str | Type[Tr]) -> bool:
        return Resolve(ident_or_type).identity in self.initialized.keys()
    
    
    def get_registered(self, ident_or_type: str | Type[Tr]) -> Type[Tr]:
        if self.has_registered(ident_or_type):
            klass = self.registered[Resolve(ident_or_type).identity]
            return cast(Type[Tr], klass)
        
        raise ValueError(f"Registrant '{ident_or_type!r}' is not registered.")
    
    def get_initialized(self, ident_or_type: str | Type[Tr]) -> Tr:
        if self.has_initialized(ident_or_type):
            return self.initialized[Resolve(ident_or_type).identity]
        raise ValueError(f"Registrant '{ident_or_type!r}' is not initialized.")
    
    def is_compatible(self, klass: Type) -> bool:
        """Check if the given class is compatible with this registry's registrant_type."""
        minimum_type = self._registrant_type()
        return (klass is minimum_type or issubclass(klass, minimum_type))
    
    def get_registrant_options(self, ident_or_type: str | Type[Tr]) -> Any:
        """Get options for a registrant by ident or type."""
        return self.get_options().get(Resolve(ident_or_type).identity, {})

    def get_options(self) -> Dict[str, Any]:
        """Get all options for this registry."""
        if self.registrar:
            return self.registrar.get_registry_options(self.__class__.kind())
        return {}
        
    # -- Main Entrypoint Methods --------------------------------------------

    def register(self, klass: Type[RegistrantAbstract]) -> Self:
        """Register a subclass of RegistrantAbstract with this typed registry."""

        # Validate Type[Tr] compatibility
        if not self.is_compatible(klass):
            raise TypeError(f"Cannot register {klass.__name__}: incompatible with registry type {self._registrant_type().__name__}")
        
        # Validate Kind compatibility
        klass_kind = Resolve(klass).kind
        if klass_kind != self.kind():
            raise ValueError(f"Cannot register {klass.__name__}: its kind ('{klass_kind}') does not match the registry's kind ('{self.kind()}')")
         
        # Register the class if not already registered
        if (ident := klass.identity()) not in self.registered:
            self.registered[ident] = klass
            
        return self
        

    
    def get(self, ident_or_type: str | Type[Tr]) -> Tr:
        """Get or initialize a _registered_ RegistrantAbstract instance by its identity or type."""
        identity = Resolve(ident_or_type).identity
            
        # Validate that the identity is registered            
        if not self.has_registered(identity):
            raise ValueError(f"RegistrantAbstract '{identity}' is not registered.")

        # Initialize (if not already) 
        if not self.has_initialized(identity):
            klass : Type[Tr] = self.get_registered(identity)
            self.initialized[identity] = klass(registry=self)
            
        return self.initialized[identity]
            
    
    @classmethod
    def _registrant_type(cls) -> Type[Tr]:
        """
        Return the specific RegistrantAbstract subclass that this registry manages.

        This method checks if the class is a subclass of Registry, if it's a parameterized
        Registry, and if the type argument is a subclass of RegistrantAbstract.

        Returns:
            Type[Tr]: The specific RegistrantAbstract subclass.

        Raises:
            TypeError: If the class is not a subclass of Registry, if it's not a parameterized
                Registry, if the type argument is not present, or if the type argument is not a
                subclass of RegistrantAbstract.
        """
        # Ensure cls is a subclass of Registry
        if not issubclass(cls, Registry):
            raise TypeError("Type is not a subclass of Registry.")

        # Need to use __orig_bases__ to as get_origin() doesn't work on subclasses
        # __orig_bases__ is a tuple of the original base classes
        
        orig_bases = getattr(cls, "__orig_bases__", None)
        
        if orig_bases is None:
            raise TypeError("Unable to determine the original bases of the class.")
        
        if not isinstance(orig_bases, tuple):
            raise TypeError("__orig_bases__ is not a tuple, bu it should be.")
        
        first_arg = None
        for base in orig_bases:
            if get_origin(base) and (args := get_args(base)):
                first_arg = args[0]
                
        if first_arg is None:
            raise TypeError("Unable to determine the first argument of the Registry class.")

        return cast(Type[Tr], first_arg)
