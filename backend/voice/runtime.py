"""Voice Runtime — Pipecat pipeline lifecycle orchestration.

Manages starting and stopping Pipecat pipeline instances.
Each session gets its own isolated pipeline.
"""

from typing import Any

from app.platform.logging import get_logger
from voice.pipeline import VoicePipeline, ConversationProcessor

logger = get_logger(__name__)


class VoiceRuntime:
    _instances: dict[str, VoicePipeline] = {}

    @classmethod
    async def start_pipeline(
        cls,
        session_id: str,
        room_name: str,
        agent_token: str,
        interaction_id: str,
        stt_provider: Any = None,
        tts_provider: Any = None,
        interaction_service: Any = None,
        complaint_service: Any = None,
        workflow_service: Any = None,
        notification_service: Any = None,
    ) -> None:
        from voice.audio import create_stt_provider, create_tts_provider

        stt = stt_provider or create_stt_provider()
        tts = tts_provider or create_tts_provider()

        logger.info(
            "voice_runtime_starting",
            session_id=session_id,
            room=room_name,
            stt_provider=type(stt).__name__,
            tts_provider=type(tts).__name__,
        )

        processor = ConversationProcessor(
            interaction_id=interaction_id,
            session_id=session_id,
            interaction_service=interaction_service,
            complaint_service=complaint_service,
            workflow_service=workflow_service,
            notification_service=notification_service,
        )

        pipeline = VoicePipeline(
            session_id=session_id,
            room_name=room_name,
            agent_token=agent_token,
            interaction_id=interaction_id,
            stt_provider=stt,
            tts_provider=tts,
            conversation_processor=processor,
        )

        cls._instances[session_id] = pipeline
        await pipeline.run()

    @classmethod
    async def stop_pipeline(
        cls,
        session_id: str,
        transport: Any = None,
    ) -> None:
        pipeline = cls._instances.pop(session_id, None)
        if pipeline:
            logger.info("voice_runtime_stopping", session_id=session_id)
            await pipeline.stop()
            logger.info("voice_runtime_stopped", session_id=session_id)
        else:
            logger.warning("voice_runtime_pipeline_not_found", session_id=session_id)

    @classmethod
    def is_running(cls, session_id: str) -> bool:
        return session_id in cls._instances

    @classmethod
    async def stop_all(cls) -> None:
        for session_id in list(cls._instances.keys()):
            await cls.stop_pipeline(session_id)
        cls._instances.clear()
