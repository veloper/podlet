"""Podlet - A type-safe dependency injection framework for Python."""

from .bootstrap import Bootstrap
from .helpers import Resolve, only_while_initializing
from .registrant import RegistrantAbstract
from .registrar import Registrar
from .registry import Registry
from .resource import ResourceAbstract, ResourceRegistry
from .types import RegistrantIdentity, RegistrantKind, Tr


__all__ = [
    # Types
    "RegistrantKind",
    "RegistrantIdentity", 
    "Tr",
    
    # Helpers
    "only_while_initializing",
    "Resolve",
    
    # Core classes
    "RegistrantAbstract",
    "Registry",
    "Registrar",
    
    # Resource-specific classes
    "ResourceAbstract",
    "ResourceRegistry",
    "Bootstrap",
]

def main() -> None:
    print("Hello from podlet!")
