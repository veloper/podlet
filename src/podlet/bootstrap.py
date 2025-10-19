from dataclasses import dataclass
from typing import List, Type, TypeVar, Union, cast

from .helpers import Resolve
from .registrar import Registrar
from .resource import ResourceAbstract, ResourceRegistry


ResourceRegistryT = TypeVar("ResourceRegistryT", bound=ResourceRegistry)
ResourceRegistrantT = TypeVar("ResourceRegistrantT", bound=ResourceAbstract)

@dataclass(init=False)
class Bootstrap(Registrar):
    """Bootstrap class, acting as a Registrar for various resource registries.
    
    Setup with a default of `resources` registry along with `get_resource` method for easy typed access.
    
    Freely extendable with additional registries as needed or usable as-is.
    
    
    Options:
        options: Dict[str, Any] - A dictionary of nested options
        {
            REGISTRY.kind(): {
                REGISTRANT.identity(): {    
                    OPTION_KEY: OPTION_VALUE
                }
            }
        }    
    """


    def __init__(self, *, resources : List[Type[ResourceRegistrantT]] = [], options = {}, ) -> None:
        super().__init__({}, options)
        
        # Register Typed Registries
        self.register_registry(ResourceRegistry) # Resource
                
        # Register provided resources
        registry = self.get_registry(ResourceAbstract)
        for resource in resources:
            registry.register(resource)

    def resources(self) -> ResourceRegistry:
        """Get the resource registry."""
        klass = self.get_registry(ResourceAbstract)
        return cast(ResourceRegistry, klass)
    
    
    def get_resource(self, ident_or_type: Union[str, Type[ResourceRegistrantT]]) -> ResourceRegistrantT:
        """Get a resource by ident or type ensuring the correct type is returned."""
        resolve = Resolve(ident_or_type)
        resource = self.get(ResourceAbstract.kind(), resolve.identity)
        expected_type = ident_or_type if isinstance(ident_or_type, type) else ResourceAbstract
        if not isinstance(resource, expected_type):
            raise TypeError(f"Ident('{resolve.identity}') is not an instance of {expected_type.__name__}")
        return cast(ResourceRegistrantT, resource)
