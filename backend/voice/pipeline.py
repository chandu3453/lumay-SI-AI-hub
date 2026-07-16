"""Voice Pipeline — Channel-agnostic Pipecat pipeline definition.

Architecture:
    Audio → STT → Conversation Engine → TTS → Audio

The pipeline has NO knowledge of LiveKit, HTTP, or any specific transport.
It receives text input (from STT) and returns text output (for TTS).
"""

import asyncio
import uuid
from typing import Any

from app.platform.logging import get_logger
from voice.transcript_manager import get_transcript_manager

logger = get_logger(__name__)


class ConversationProcessor:
    def __init__(
        self,
        interaction_id: str,
        session_id: str,
        interaction_service: Any = None,
        complaint_service: Any = None,
        workflow_service: Any = None,
        notification_service: Any = None,
    ) -> None:
        self._interaction_id = interaction_id
        self._session_id = session_id
        self._interaction_service = interaction_service
        self._complaint_service = complaint_service
        self._workflow_service = workflow_service
        self._notification_service = notification_service

    async def process_text(self, text: str) -> str:
        tm = get_transcript_manager()
        await tm.add_segment(self._session_id, "customer", text, is_partial=False)

        try:
            from domains.interaction.services.conversation_engine import (
                process_conversation,
            )

            result = await process_conversation(
                interaction_id=uuid.UUID(self._interaction_id),
                message=text,
                interaction_service=self._interaction_service,
                complaint_service=self._complaint_service,
                workflow_service=self._workflow_service,
                notification_service=self._notification_service,
            )

            ai_response = result.get("answer", "")
            await tm.add_segment(
                self._session_id, "assistant", ai_response, is_partial=False
            )

            if result.get("auto_triaged"):
                complaint_id = result.get("complaint_id")
                workflow_id = result.get("workflow_id")
                if complaint_id:
                    tm.update_metadata(self._session_id, "complaint_id", str(complaint_id))
                if workflow_id:
                    tm.update_metadata(self._session_id, "workflow_id", str(workflow_id))

            return ai_response

        except Exception as exc:
            logger.error(
                "voice_conversation_engine_failed",
                session_id=self._session_id,
                error=str(exc),
            )
            fallback = (
                "I apologise, but I am experiencing a temporary technical issue. "
                "Your message has been recorded and a member of our team will follow up with you shortly. "
                "For urgent matters, please call 800-LUMAY-1."
            )
            await tm.add_segment(
                self._session_id, "assistant", fallback, is_partial=False
            )
            return fallback


class VoicePipeline:
    def __init__(
        self,
        session_id: str,
        room_name: str,
        agent_token: str,
        interaction_id: str,
        stt_provider: Any,
        tts_provider: Any,
        conversation_processor: ConversationProcessor,
    ) -> None:
        self._session_id = session_id
        self._room_name = room_name
        self._agent_token = agent_token
        self._interaction_id = interaction_id
        self._stt = stt_provider
        self._tts = tts_provider
        self._processor = conversation_processor
        self._pipeline_instance: Any = None
        self._runner_instance: Any = None
        self._transport_instance: Any = None

    async def run(self) -> None:
        logger.info(
            "voice_pipeline_starting",
            session_id=self._session_id,
            room=self._room_name,
        )

        try:
            from pipecat.pipeline.pipeline import Pipeline
            from pipecat.pipeline.runner import PipelineRunner
            from pipecat.transports.livekit.transport import LiveKitTransport as PipecatLiveKitTransport
            from pipecat.transports.livekit.transport import LiveKitParams

            from voice.config import VoiceConfig
            _vc = VoiceConfig()

            logger.info("voice_pipeline_creating_transport", session_id=self._session_id, room=self._room_name)
            transport = PipecatLiveKitTransport(
                url=_vc.livekit_url,
                token=self._agent_token,
                room_name=self._room_name,
                params=LiveKitParams(audio_in_enabled=True, audio_out_enabled=True),
            )

            from voice.audio import AzureSTTProvider, AzureTTSProvider

            logger.info("voice_pipeline_creating_stt", session_id=self._session_id, stt_type=type(self._stt).__name__)
            if isinstance(self._stt, AzureSTTProvider):
                from pipecat.services.azure.stt import AzureSTTService as PipecatSTT
                stt_service = PipecatSTT(
                    api_key=self._stt._key,
                    region=self._stt._region,
                    private_endpoint=self._stt._endpoint,
                )
                import azure.cognitiveservices.speech as speechsdk
                # 1. Set general end silence property
                stt_service._speech_config.set_property(
                    speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "2000"
                )
                # 2. Enforce continuous recognition silence timeout to 2.0s
                stt_service._speech_config.set_property(
                    speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, "2000"
                )
                # 3. Enable semantic endpointing to wait for complete sentences
                stt_service._speech_config.set_property(
                    speechsdk.PropertyId.Speech_SegmentationStrategy, "Semantic"
                )
            else:
                from pipecat.services.deepgram.stt import DeepgramSTTService as PipecatSTT
                import os
                dg_key = os.getenv("DEEPGRAM_API_KEY", "")
                logger.info("voice_pipeline_stt_deepgram", session_id=self._session_id, key_configured=bool(dg_key))
                stt_service = PipecatSTT(
                    api_key=dg_key,
                    settings=PipecatSTT.Settings(
                        endpointing=2200,       # Wait 2.2 seconds of silence before finalizing user's speech!
                        utterance_end_ms=2200,  # Match utterance gap timeout
                    )
                )

            logger.info("voice_pipeline_creating_tts", session_id=self._session_id, tts_type=type(self._tts).__name__)
            if isinstance(self._tts, AzureTTSProvider):
                from pipecat.services.azure.tts import AzureTTSService as PipecatTTS
                tts_service = PipecatTTS(
                    api_key=self._tts._key,
                    region=self._tts._region,
                    private_endpoint=self._tts._endpoint,
                    voice=self._tts._voice,
                )
            else:
                from pipecat.services.deepgram.tts import DeepgramTTSService as PipecatTTS
                import os
                dg_key = os.getenv("DEEPGRAM_API_KEY", "")
                logger.info("voice_pipeline_tts_deepgram", session_id=self._session_id, key_configured=bool(dg_key))
                tts_service = PipecatTTS(
                    api_key=dg_key,
                    voice="aura-2-helena-en",  # Use the cleaner, smoother, and natural Aura v2 voice!
                )

            class PipecatLLMProcessor:
                def __init__(self, processor: ConversationProcessor) -> None:
                    self._processor = processor

                async def process_text(self, text: str) -> str:
                    return await self._processor.process_text(text)

            llm_processor = PipecatLLMProcessor(self._processor)

            from pipecat.processors.frame_processor import FrameProcessor
            from pipecat.frames.frames import (
                TextFrame, StartFrame, TranscriptionFrame, AudioRawFrame,
                LLMFullResponseStartFrame, LLMFullResponseEndFrame,
                InterimTranscriptionFrame, EndFrame, CancelFrame,
            )

            class ConversationFrameworkProcessor(FrameProcessor):
                def __init__(self, llm: PipecatLLMProcessor) -> None:
                    super().__init__()
                    self._llm = llm
                    self.first_audio_event = asyncio.Event()
                    self._turn_buffer = []
                    self._turn_dispatch_task = None

                def _cancel_dispatch_task(self) -> None:
                    if self._turn_dispatch_task and not self._turn_dispatch_task.done():
                        self._turn_dispatch_task.cancel()
                        self._turn_dispatch_task = None

                async def _wait_and_dispatch_turn(self) -> None:
                    # Wait for 1.8 seconds of complete silence before dispatching
                    await asyncio.sleep(1.8)
                    if self._turn_buffer:
                        full_text = " ".join(self._turn_buffer).strip()
                        self._turn_buffer.clear()
                        if full_text:
                            logger.info("voice_pipeline_dispatching_aggregated_turn", text=full_text)
                            import time
                            turn_start = time.monotonic()
                            response = await self._llm.process_text(full_text)
                            total_latency = (time.monotonic() - turn_start) * 1000
                            logger.info("voice_pipeline_total_turn_latency", latency_ms=total_latency, transcript=full_text)
                            await self._push_response(response)

                def _sanitize_for_tts(self, text: str) -> str:
                    import re
                    # 1. Clean bold/italic markdown formatting
                    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
                    text = re.sub(r'\*([^*]+)\*', r'\1', text)
                    text = re.sub(r'__([^_]+)__', r'\1', text)
                    text = re.sub(r'_([^_]+)_', r'\1', text)
                    
                    # 2. Clean markdown links: [label](url) -> label
                    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
                    
                    # 3. Clean headers (e.g. # Title)
                    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
                    
                    # 4. Clean bullet lists: remove leading -, *, +
                    text = re.sub(r'^[-\*\+]\s+', '', text, flags=re.MULTILINE)
                    
                    # 5. Convert numbered lists conversationally:
                    pattern = r'(?:^\d+\.\s+.*(?:\n|$))+'
                    matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
                    
                    for match in reversed(matches):
                        block = match.group(0)
                        items = [re.sub(r'^\d+\.\s+', '', line).strip() for line in block.strip().split('\n') if line.strip()]
                        if len(items) == 1:
                            replacement = items[0]
                        elif len(items) == 2:
                            replacement = f"{items[0]} and {items[1]}"
                        else:
                            replacement = ", ".join(items[:-1]) + f", and {items[-1]}"
                        
                        if not replacement.endswith('.'):
                            replacement += '.'
                        
                        text = text[:match.start()] + replacement + text[match.end():]
                        
                    # 6. Replace multiple newlines or spaces with a single space
                    text = re.sub(r'\s+', ' ', text)
                    return text.strip()

                async def _push_response(self, response: str) -> None:
                    """Push LLM response split into sentences to enable faster streaming TTS start."""
                    await self.push_frame(LLMFullResponseStartFrame())
                    speech_text = self._sanitize_for_tts(response)
                    import re
                    sentences = re.split(r'(?<=[.!?])\s+', speech_text)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if sentence:
                            await self.push_frame(TextFrame(sentence))
                            await asyncio.sleep(0.01)
                    await self.push_frame(LLMFullResponseEndFrame())

                async def process_frame(self, frame: Any, direction: Any) -> None:
                    await super().process_frame(frame, direction)
                    if isinstance(frame, StartFrame):
                        self.first_audio_event.set()
                        await self.push_frame(frame)
                        prompt = (
                            "SYSTEM_INTERNAL: The user has just connected to the call. "
                            "Introduce yourself exactly as: 'Hello, welcome to LuMay Insurance. I'm the LuMay AI Assistant. How can I help you today?'"
                        )
                        response = await self._llm.process_text(prompt)
                        await self._push_response(response)
                    elif isinstance(frame, TranscriptionFrame):
                        self.first_audio_event.set()
                        self._turn_buffer.append(frame.text.strip())
                        self._cancel_dispatch_task()
                        self._turn_dispatch_task = asyncio.create_task(self._wait_and_dispatch_turn())
                    elif isinstance(frame, InterimTranscriptionFrame):
                        self._cancel_dispatch_task()
                    elif isinstance(frame, EndFrame) or isinstance(frame, CancelFrame):
                        self._cancel_dispatch_task()
                    elif isinstance(frame, AudioRawFrame):
                        # Discard user audio raw frames to prevent echo loopback to transport.output()
                        pass
                    else:
                        await self.push_frame(frame)

            framework = ConversationFrameworkProcessor(llm_processor)

            logger.info("voice_pipeline_assembling", session_id=self._session_id)
            pipeline = Pipeline([
                transport.input(),
                stt_service,
                framework,
                tts_service,
                transport.output(),
            ])

            from pipecat.pipeline.task import PipelineTask

            runner = PipelineRunner()
            task = PipelineTask(pipeline)
            self._pipeline_instance = pipeline
            self._runner_instance = runner
            self._task_instance = task
            self._transport_instance = transport

            tm = get_transcript_manager()

            runner_task = asyncio.create_task(runner.run(task))
            connect_timeout = _vc.pipeline_connect_timeout

            logger.info(
                "voice_pipeline_awaiting_participant",
                session_id=self._session_id,
                room=self._room_name,
                connect_timeout_seconds=connect_timeout,
            )
            try:
                await asyncio.wait_for(
                    framework.first_audio_event.wait(),
                    timeout=connect_timeout,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "voice_pipeline_connect_timeout",
                    session_id=self._session_id,
                    timeout_seconds=connect_timeout,
                )
                await tm.update_status(self._session_id, "timeout")
                await tm.add_segment(
                    self._session_id,
                    "system",
                    "No participant joined within the connection timeout period.",
                )
                runner_task.cancel()
                return

            await tm.update_status(self._session_id, "connected")
            logger.info(
                "voice_pipeline_participant_joined",
                session_id=self._session_id,
                room=self._room_name,
            )

            max_duration = _vc.max_session_duration
            logger.info(
                "voice_pipeline_running",
                session_id=self._session_id,
                max_duration_seconds=max_duration,
            )
            await asyncio.wait_for(runner_task, timeout=max_duration)

        except asyncio.TimeoutError:
            logger.warning(
                "voice_pipeline_session_timeout",
                session_id=self._session_id,
                max_duration_seconds=_vc.max_session_duration,
            )
            tm = get_transcript_manager()
            await tm.add_segment(
                self._session_id,
                "system",
                "Session timed out after maximum duration.",
            )
        except ImportError as exc:
            logger.error(
                "pipecat_import_error",
                error=str(exc),
                hint="Install pipecat-ai[azure] and livekit-api",
            )
            tm = get_transcript_manager()
            await tm.update_status(self._session_id, "error")
            await tm.add_segment(self._session_id, "system", f"Pipecat unavailable: {exc}")
        except Exception as exc:
            logger.error(
                "voice_pipeline_failed",
                session_id=self._session_id,
                error=str(exc),
            )
            tm = get_transcript_manager()
            await tm.update_status(self._session_id, "error")
            await tm.add_segment(self._session_id, "system", f"Pipeline error: {exc}")
        finally:
            tm = get_transcript_manager()
            await tm.end_session(self._session_id)
            logger.info(
                "voice_pipeline_ended",
                session_id=self._session_id,
                room=self._room_name,
            )

    async def stop(self) -> None:
        if hasattr(self, "_task_instance") and self._task_instance:
            try:
                from pipecat.frames.frames import EndFrame
                await self._task_instance.queue_frame(EndFrame())
                logger.info("voice_pipeline_stopped", session_id=self._session_id)
            except Exception as exc:
                logger.warning(
                    "voice_pipeline_stop_error",
                    session_id=self._session_id,
                    error=str(exc),
                )
        self._pipeline_instance = None
        self._task_instance = None
        self._runner_instance = None
        self._transport_instance = None
