"""Session Manager.

Handles voice session lifecycle:
    Create Session (room + interaction + tokens)
    End Session (stop pipeline + cleanup room + complete interaction)
    Session Status
"""

import uuid
from typing import Any

from app.platform.logging import get_logger
from voice.transcript_manager import get_transcript_manager
from voice.config import VoiceConfig
from voice.transport import LiveKitTransport

logger = get_logger(__name__)


class SessionManager:
    def __init__(
        self,
        transport: LiveKitTransport | None = None,
        interaction_service: Any = None,
        complaint_service: Any = None,
        workflow_service: Any = None,
        notification_service: Any = None,
    ) -> None:
        self._transport = transport or LiveKitTransport()
        self._config = VoiceConfig()
        self._interaction_service = interaction_service
        self._complaint_service = complaint_service
        self._workflow_service = workflow_service
        self._notification_service = notification_service
        self._active_pipelines: dict[str, Any] = {}

    async def create_session(
        self,
        customer_ref: str | None = None,
        room_name: str | None = None,
    ) -> dict[str, Any]:
        actual_room = room_name or f"voice-{uuid.uuid4().hex[:12]}"
        logger.info(
            "session_creating",
            room=actual_room,
            customer_ref=customer_ref,
        )
        await self._transport.create_room(
            name=actual_room,
            max_participants=2,
            empty_timeout=60,
        )

        participant_token = self._transport.generate_participant_token(
            room_name=actual_room,
            identity=f"caller-{uuid.uuid4().hex[:8]}",
            participant_name="Customer",
        )
        logger.debug("session_participant_token_generated", room=actual_room)

        agent_token = self._transport.generate_agent_token(room_name=actual_room)
        logger.debug("session_agent_token_generated", room=actual_room)
        session_id = uuid.uuid4().hex[:16]

        from domains.interaction.constants.interaction_constants import (
            InteractionChannel,
            InteractionDirection,
            InteractionStatus,
        )
        from domains.interaction.schemas.interaction_schemas import (
            InteractionCreate,
        )

        interaction_create = InteractionCreate(
            customer_ref=customer_ref,
            channel=InteractionChannel.VOICE,
            direction=InteractionDirection.INBOUND,
            subject="Voice Call Session",
            transcript="[]",
            status=InteractionStatus.RECEIVED,
        )

        try:
            interaction, _ = await self._interaction_service.create_interaction(
                interaction_create
            )
            interaction_id = str(interaction.id)

            from domains.conversation import integration_hooks as conversation_hooks

            conversation_id = await conversation_hooks.on_interaction_started(
                self._interaction_service._repository._session,
                customer_ref,
                "voice",
                interaction.id,
            )
            await conversation_hooks.on_voice_session_started(
                self._interaction_service._repository._session,
                conversation_id,
                actual_room,
            )
        except Exception as exc:
            logger.warning("session_interaction_create_failed", error=str(exc))
            interaction_id = str(uuid.uuid4())

        tm = get_transcript_manager()
        await tm.create_session(
            session_id=session_id,
            interaction_id=interaction_id,
            room_name=actual_room,
            customer_ref=customer_ref,
        )

        return {
            "session_id": session_id,
            "interaction_id": interaction_id,
            "room_name": actual_room,
            "participant_token": participant_token,
            "agent_token": agent_token,
            "livekit_url": self._config.livekit_url,
        }

    async def end_session(self, session_id: str) -> dict[str, Any]:
        logger.info("session_ending", session_id=session_id)
        from voice.runtime import VoiceRuntime

        await VoiceRuntime.stop_pipeline(session_id, self._transport)
        self._active_pipelines.pop(session_id, None)

        tm = get_transcript_manager()
        session = tm.get_session(session_id)

        if session:
            # Marks status="ended" and stamps ended_at — needed so the
            # voice.session_ended conversation event below can compute a
            # duration. (This was previously never called at all: session
            # dicts carried a started_at but no ended_at ever got set.)
            await tm.end_session(session_id)

            if self._interaction_service:
                from domains.interaction.constants.interaction_constants import (
                    InteractionStatus,
                )
                from domains.interaction.schemas.interaction_schemas import (
                    InteractionUpdate,
                )
                try:
                    await tm.append_to_interaction(
                        session_id, self._interaction_service
                    )
                    await self._interaction_service.update_interaction(
                        uuid.UUID(session["interaction_id"]),
                        InteractionUpdate(status=InteractionStatus.COMPLETED),
                    )

                    from domains.conversation import integration_hooks as conversation_hooks

                    await conversation_hooks.on_voice_session_ended(
                        self._interaction_service._repository._session,
                        session["interaction_id"],
                        session.get("started_at"),
                        session.get("ended_at"),
                        room_name=session.get("room_name"),
                    )
                except Exception as exc:
                    logger.warning(
                        "session_interaction_update_error",
                        session_id=session_id,
                        error=str(exc),
                    )

            try:
                await self._transport.delete_room(session.get("room_name", ""))
            except Exception as exc:
                logger.warning(
                    "session_room_deletion_error",
                    room=session.get("room_name"),
                    error=str(exc),
                )

        return {
            "session_id": session_id,
            "status": "ended",
            "transcript": tm.get_transcript(session_id),
        }

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        tm = get_transcript_manager()
        return tm.get_session(session_id)

    async def get_transcript(self, session_id: str) -> list[dict[str, Any]]:
        tm = get_transcript_manager()
        return tm.get_transcript(session_id)

    def register_pipeline(self, session_id: str, pipeline: Any) -> None:
        self._active_pipelines[session_id] = pipeline

    def is_pipeline_running(self, session_id: str) -> bool:
        return session_id in self._active_pipelines
