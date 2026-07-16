"""
Conversation memory — stores and retrieves multi-turn conversation history.

Manages per-session message history with configurable window sizes
and strategies (sliding window, token-based, summary-based).
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MemoryStrategy(StrEnum):
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BOUNDED = "token_bounded"
    SUMMARY_BASED = "summary_based"
    UNLIMITED = "unlimited"


@dataclass(frozen=True)
class Message:
    """A single message in a conversation.

    Attributes:
        role:     Message role (user, assistant, system).
        content:  Message text content.
        metadata: Additional message metadata (timestamp, tokens, etc.).
    """

    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConversationHistory:
    """Full conversation history for a session.

    Attributes:
        session_id: Unique session identifier.
        messages:   Ordered list of messages (oldest first).
        summary:    Optional compressed summary of the conversation.
    """

    session_id: str
    messages: list[Message]
    summary: str | None = None


class ConversationMemory:
    """Manages conversation history per session.

    Args:
        strategy:  Memory retention strategy.
        max_size:  Maximum messages or tokens (depends on strategy).
        ttl_minutes: Session TTL in minutes (None = no expiry).
    """

    def __init__(
        self,
        strategy: MemoryStrategy = MemoryStrategy.SLIDING_WINDOW,
        max_size: int = 50,
        ttl_minutes: int | None = 60,
    ) -> None:
        ...

    async def add_message(self, session_id: str, message: Message) -> None:
        """Appends a message to the session history."""
        ...

    async def get_history(self, session_id: str) -> ConversationHistory:
        """Returns the full conversation history for a session."""
        ...

    async def clear(self, session_id: str) -> None:
        """Clears all history for a session."""
        ...
