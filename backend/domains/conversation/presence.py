"""Presence & typing registry (Sprint 28 Phase 4).

In-process, ephemeral state — structurally identical to
`voice/transcript_manager.py`'s `TranscriptManager`: presence/typing are
live-only signals, not an audit trail, so they're never written to
`conversation_events` (that would spam the timeline on every keystroke).
Detection is explicit client pings (mount/heartbeat/unmount), not derived
from SSE connection lifecycle — simpler, and "update using SSE" describes how
*other* clients learn about a change, not how the change is detected.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from app.platform.logging import get_logger

logger = get_logger(__name__)

# A presence ping older than this is treated as stale/offline — guards against
# a client that never sent an explicit "offline" (tab closed without
# unmount/beforeunload firing, network drop, etc.).
_PRESENCE_STALE_AFTER = timedelta(seconds=45)
# Typing indicators auto-expire fast — no explicit "stopped typing" ping is
# required for correctness, only for a snappier UI.
_TYPING_STALE_AFTER = timedelta(seconds=6)


class PresenceRegistry:
    def __init__(self) -> None:
        # conversation_id -> participant_type -> participant_ref -> {status, last_seen}
        self._presence: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
        # conversation_id -> participant_type -> {is_typing, last_seen}
        self._typing: dict[str, dict[str, dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def set_presence(
        self, conversation_id: str, participant_type: str, participant_ref: str, status: str
    ) -> None:
        async with self._lock:
            conv = self._presence.setdefault(conversation_id, {})
            by_ref = conv.setdefault(participant_type, {})
            by_ref[participant_ref] = {"status": status, "last_seen": datetime.now(UTC)}
        logger.debug(
            "conversation_presence_set",
            conversation_id=conversation_id,
            participant_type=participant_type,
            status=status,
        )

    async def set_typing(self, conversation_id: str, participant_type: str, is_typing: bool) -> None:
        async with self._lock:
            conv = self._typing.setdefault(conversation_id, {})
            conv[participant_type] = {"is_typing": is_typing, "last_seen": datetime.now(UTC)}

    def get_snapshot(self, conversation_id: str) -> dict[str, Any]:
        """Presence entries older than `_PRESENCE_STALE_AFTER` are reported as
        offline; typing entries older than `_TYPING_STALE_AFTER` are reported
        as not-typing — both without needing a background sweep."""
        now = datetime.now(UTC)
        presence: dict[str, dict[str, str]] = {}
        for participant_type, by_ref in self._presence.get(conversation_id, {}).items():
            presence[participant_type] = {
                ref: (
                    "online"
                    if entry["status"] == "online"
                    and now - entry["last_seen"] <= _PRESENCE_STALE_AFTER
                    else "offline"
                )
                for ref, entry in by_ref.items()
            }

        typing: dict[str, bool] = {}
        for participant_type, entry in self._typing.get(conversation_id, {}).items():
            typing[participant_type] = bool(entry["is_typing"]) and (
                now - entry["last_seen"] <= _TYPING_STALE_AFTER
            )

        return {"presence": presence, "typing": typing}

    async def clear_conversation(self, conversation_id: str) -> None:
        async with self._lock:
            self._presence.pop(conversation_id, None)
            self._typing.pop(conversation_id, None)

    def count_online_employees(self) -> int:
        """Sprint 29 — Supervisor Dashboard's "Employees Online". Scans every
        tracked conversation's presence map for distinct online `employee`
        refs. Same accepted limitation as the rest of this registry:
        in-process, single-worker, ephemeral — an approximation, not a
        durable presence system."""
        now = datetime.now(UTC)
        online_refs: set[str] = set()
        for by_ref in (conv.get("employee", {}) for conv in self._presence.values()):
            for ref, entry in by_ref.items():
                if entry["status"] == "online" and now - entry["last_seen"] <= _PRESENCE_STALE_AFTER:
                    online_refs.add(ref)
        return len(online_refs)


_presence_registry = PresenceRegistry()


def get_presence_registry() -> PresenceRegistry:
    return _presence_registry
