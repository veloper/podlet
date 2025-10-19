"""Type definitions and aliases for the Podlet DI framework."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypeVar


if TYPE_CHECKING:
    from .registrant import RegistrantAbstract


# Type aliases that should be 100% interchangeable with a str literal
RegistrantKind: TypeAlias = str
RegistrantIdentity: TypeAlias = str

# Type variables for generic constraints
Tr = TypeVar("Tr", bound="RegistrantAbstract", covariant=True)
