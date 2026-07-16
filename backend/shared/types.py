"""
Shared Type Aliases.

Common types used across domains to avoid duplication.
"""

import uuid
from typing import TypeAlias

EntityId: TypeAlias = uuid.UUID
Email: TypeAlias = str
PhoneNumber: TypeAlias = str
JsonDict: TypeAlias = dict[str, object]
