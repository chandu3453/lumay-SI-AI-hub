"""Transcript Manager.

Continuously streams customer and AI transcript segments.
Stores conversation metadata (ID, timestamp, channel, customer, policy, complaint).
Appends transcript to existing interaction history.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.platform.logging import get_logger

logger = get_logger(__name__)


class TranscriptManager:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        session_id: str,
        interaction_id: str,
        room_name: str,
        customer_ref: str | None = None,
        channel: str = "voice",
    ) -> None:
        async with self._lock:
            self._sessions[session_id] = {
                "session_id": session_id,
                "interaction_id": interaction_id,
                "room_name": room_name,
                "customer_ref": customer_ref,
                "channel": channel,
                "status": "connecting",
                "transcript_segments": [],
                "started_at": datetime.now(timezone.utc).isoformat(),
                "ended_at": None,
                "error": None,
                "metadata": {
                    "policy_number": None,
                    "complaint_id": None,
                    "customer_name": None,
                },
            }
        logger.info(
            "transcript_session_created",
            session_id=session_id,
            interaction_id=interaction_id,
            room=room_name,
        )

    async def update_status(self, session_id: str, status: str) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session["status"] = status

    async def add_segment(
        self,
        session_id: str,
        role: str,
        text: str,
        is_partial: bool = False,
    ) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.warning("transcript_segment_dropped_no_session", session_id=session_id, role=role)
                return
            segment = {
                "role": role,
                "text": text,
                "is_partial": is_partial,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            session["transcript_segments"].append(segment)
        logger.debug(
            "transcript_segment_added",
            session_id=session_id,
            role=role,
            is_partial=is_partial,
            length=len(text),
        )

    async def update_metadata(self, session_id: str, key: str, value: Any) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session and "metadata" in session:
                session["metadata"][key] = value

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    def get_transcript(self, session_id: str) -> list[dict[str, Any]]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.get("transcript_segments", [])

    async def end_session(self, session_id: str) -> dict[str, Any] | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session["status"] = "ended"
                session["ended_at"] = datetime.now(timezone.utc).isoformat()
            return session

    async def remove_session(self, session_id: str) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def cleanup_stale_sessions(self, max_age_minutes: int = 30) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        stale = []
        async with self._lock:
            for sid, session in self._sessions.items():
                ended = session.get("ended_at")
                if ended:
                    ended_dt = datetime.fromisoformat(ended)
                    if ended_dt < cutoff:
                        stale.append(sid)
                elif session["status"] in ("ended", "error"):
                    started = session.get("started_at")
                    if started and datetime.fromisoformat(started) < cutoff:
                        stale.append(sid)
            for sid in stale:
                del self._sessions[sid]
        if stale:
            logger.info("stale_sessions_cleaned", count=len(stale))
        return len(stale)

    async def append_to_interaction(
        self,
        session_id: str,
        interaction_service: Any,
    ) -> None:
        session = self._sessions.get(session_id)
        if not session or not interaction_service:
            return
        try:
            from domains.interaction.schemas.interaction_schemas import (
                InteractionUpdate,
            )

            interaction_id = uuid.UUID(session["interaction_id"])
            interaction = await interaction_service.get_interaction(interaction_id)
            if not interaction:
                return
            history = []
            if interaction.transcript:
                try:
                    history = json.loads(interaction.transcript)
                except (json.JSONDecodeError, TypeError):
                    history = []
            from domains.conversation import integration_hooks as conversation_hooks
            from domains.conversation.constants.conversation_constants import (
                ConversationMessageType,
            )

            # Each turn is already persisted to Interaction.transcript live,
            # per-turn, by conversation_engine._finalize_turn (the same
            # mechanism text chat uses) as long as the pipeline's own DB
            # session commits at call end (see voice/router.py's
            # _run_pipeline_isolated). This end-of-call flush exists only as
            # a safety net for the rare case that commit never ran (crash,
            # kill, cross-process TranscriptManager). Slicing to segments
            # beyond len(history) keeps it a no-op in the normal case instead
            # of duplicating every message on top of what's already there.
            finalized = [
                seg for seg in session.get("transcript_segments", [])
                if not seg.get("is_partial", False)
            ]
            new_segments = finalized[len(history):]
            for seg in new_segments:
                role = "user" if seg["role"] == "customer" else "assistant"
                history.append({
                    "role": role,
                    "content": seg["text"],
                    "timestamp": seg["timestamp"],
                })
                await conversation_hooks.on_message(
                    interaction_service._repository._session,
                    interaction_id,
                    role,
                    "voice",
                    seg["text"],
                    message_type=ConversationMessageType.TRANSCRIPT,
                )
            if new_segments:
                await interaction_service.update_interaction(
                    interaction_id,
                    InteractionUpdate(transcript=json.dumps(history)),
                )
        except Exception as exc:
            logger.error(
                "transcript_append_failed",
                session_id=session_id,
                error=str(exc),
            )


_transcript_manager = TranscriptManager()


def get_transcript_manager() -> TranscriptManager:
    return _transcript_manager
