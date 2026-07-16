"""
Shared Type Aliases.

Common type definitions reused across the platform.
"""

import uuid
from typing import TypeAlias

EntityId: TypeAlias = uuid.UUID
Email: TypeAlias = str
PhoneNumber: TypeAlias = str
JsonDict: TypeAlias = dict[str, object]
