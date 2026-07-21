"""Voice Pipeline — Channel-agnostic Pipecat pipeline definition.

Architecture:
    Audio → STT → Conversation Engine → TTS → Audio

The pipeline has NO knowledge of LiveKit, HTTP, or any specific transport.
It receives text input (from STT) and returns text output (for TTS).
"""

import asyncio
import uuid
from typing import Any, AsyncGenerator

from app.platform.logging import get_logger
from voice.transcript_manager import get_transcript_manager

logger = get_logger(__name__)

_FALLBACK_MESSAGE = (
    "I apologise, but I am experiencing a temporary technical issue. "
    "Your message has been recorded and a member of our team will follow up with you shortly. "
    "For urgent matters, please call 800-LUMAY-1."
)


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
            await tm.add_segment(
                self._session_id, "assistant", _FALLBACK_MESSAGE, is_partial=False
            )
            return _FALLBACK_MESSAGE

    async def process_text_stream(self, text: str) -> AsyncGenerator[str, None]:
        """Streaming counterpart of process_text — yields response text as it
        arrives from the AI gateway instead of waiting for the full reply, so
        the caller can start TTS on the first sentence immediately."""
        tm = get_transcript_manager()
        await tm.add_segment(self._session_id, "customer", text, is_partial=False)

        from domains.interaction.services.conversation_engine import (
            process_conversation_stream,
        )

        full_response = ""
        try:
            async for event in process_conversation_stream(
                interaction_id=uuid.UUID(self._interaction_id),
                message=text,
                interaction_service=self._interaction_service,
                complaint_service=self._complaint_service,
                workflow_service=self._workflow_service,
                notification_service=self._notification_service,
            ):
                if event["type"] == "chunk":
                    full_response += event["text"]
                    yield event["text"]
                elif event["type"] == "done":
                    if event.get("auto_triaged"):
                        complaint_id = event.get("complaint_id")
                        workflow_id = event.get("workflow_id")
                        if complaint_id:
                            await tm.update_metadata(self._session_id, "complaint_id", str(complaint_id))
                        if workflow_id:
                            await tm.update_metadata(self._session_id, "workflow_id", str(workflow_id))

            await tm.add_segment(
                self._session_id, "assistant", full_response, is_partial=False
            )
        except Exception as exc:
            logger.error(
                "voice_conversation_engine_stream_failed",
                session_id=self._session_id,
                error=str(exc),
            )
            await tm.add_segment(
                self._session_id, "assistant", _FALLBACK_MESSAGE, is_partial=False
            )
            yield _FALLBACK_MESSAGE


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
            from pipecat.audio.vad.silero import SileroVADAnalyzer
            from pipecat.audio.vad.vad_analyzer import VADParams
            from pipecat.processors.audio.vad_processor import VADProcessor

            from voice.config import VoiceConfig
            _vc = VoiceConfig()

            logger.info("voice_pipeline_creating_transport", session_id=self._session_id, room=self._room_name)
            transport = PipecatLiveKitTransport(
                url=_vc.livekit_url,
                token=self._agent_token,
                room_name=self._room_name,
                params=LiveKitParams(audio_in_enabled=True, audio_out_enabled=True),
            )

            logger.info("voice_pipeline_creating_vad", session_id=self._session_id)
            vad_processor = VADProcessor(
                vad_analyzer=SileroVADAnalyzer(
                    params=VADParams(
                        confidence=_vc.vad_confidence,
                        start_secs=_vc.vad_start_secs,
                        stop_secs=_vc.vad_stop_secs,
                        min_volume=_vc.vad_min_volume,
                    ),
                ),
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

                def process_text_stream(self, text: str):
                    return self._processor.process_text_stream(text)

            llm_processor = PipecatLLMProcessor(self._processor)

            from pipecat.processors.frame_processor import FrameProcessor
            from pipecat.frames.frames import (
                TextFrame, StartFrame, TranscriptionFrame, AudioRawFrame,
                LLMFullResponseStartFrame, LLMFullResponseEndFrame,
                InterimTranscriptionFrame, EndFrame, CancelFrame,
                VADUserStartedSpeakingFrame, VADUserStoppedSpeakingFrame,
            )

            # Grace window after a VAD-confirmed "user stopped speaking" event
            # before dispatching the turn — VAD is now the primary turn-taking
            # signal (replaces the old fixed 1.8s post-transcript debounce).
            _VAD_GRACE_SECS = 0.5
            # Safety-net grace window used only if no recent VAD-stop signal
            # exists (e.g. VAD misfires) — still faster than the old 1.8s.
            _FALLBACK_GRACE_SECS = 1.2
            _VAD_RECENCY_WINDOW_SECS = 3.0

            class ConversationFrameworkProcessor(FrameProcessor):
                def __init__(self, llm: PipecatLLMProcessor) -> None:
                    super().__init__()
                    self._llm = llm
                    self.first_audio_event = asyncio.Event()
                    self._turn_buffer: list[str] = []
                    self._dispatch_task: asyncio.Task | None = None
                    self._generation_task: asyncio.Task | None = None
                    self._agent_speaking = False
                    self._last_vad_stop_at: float | None = None

                def _cancel_dispatch_task(self) -> None:
                    if self._dispatch_task and not self._dispatch_task.done():
                        self._dispatch_task.cancel()
                    self._dispatch_task = None

                def _cancel_generation(self) -> None:
                    if self._generation_task and not self._generation_task.done():
                        self._generation_task.cancel()
                    self._generation_task = None
                    self._agent_speaking = False

                async def _grace_then_dispatch(self, grace_secs: float) -> None:
                    await asyncio.sleep(grace_secs)
                    if not self._turn_buffer:
                        return
                    full_text = " ".join(self._turn_buffer).strip()
                    self._turn_buffer.clear()
                    if full_text:
                        logger.info("voice_pipeline_dispatching_aggregated_turn", text=full_text, grace_secs=grace_secs)
                        self._generation_task = asyncio.create_task(self._dispatch_turn(full_text))

                async def _dispatch_turn(self, text: str) -> None:
                    """Streams the AI response and pushes complete sentences to
                    TTS as they form, instead of waiting for the full reply —
                    cancellable mid-flight for barge-in (see broadcast_interruption
                    below)."""
                    import re
                    import time

                    self._agent_speaking = True
                    turn_start = time.monotonic()
                    ttft_logged = False
                    sentence_buffer = ""
                    try:
                        await self.push_frame(LLMFullResponseStartFrame())
                        async for chunk in self._llm.process_text_stream(text):
                            if not ttft_logged:
                                ttft_logged = True
                                ttft_ms = (time.monotonic() - turn_start) * 1000
                                logger.info("voice_pipeline_turn_ttft_ms", latency_ms=ttft_ms, transcript=text)
                            sentence_buffer += chunk
                            while True:
                                match = re.search(r"(?<=[.!?])\s+", sentence_buffer)
                                if not match:
                                    break
                                sentence = sentence_buffer[: match.start()].strip()
                                sentence_buffer = sentence_buffer[match.end():]
                                if sentence:
                                    clean = self._sanitize_for_tts(sentence)
                                    if clean:
                                        await self.push_frame(TextFrame(clean))
                        remaining = sentence_buffer.strip()
                        if remaining:
                            clean = self._sanitize_for_tts(remaining)
                            if clean:
                                await self.push_frame(TextFrame(clean))
                        await self.push_frame(LLMFullResponseEndFrame())
                        total_latency = (time.monotonic() - turn_start) * 1000
                        logger.info("voice_pipeline_total_turn_latency", latency_ms=total_latency, transcript=text)
                    except asyncio.CancelledError:
                        logger.info("voice_pipeline_turn_interrupted", transcript=text)
                        raise
                    finally:
                        self._agent_speaking = False

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

                async def process_frame(self, frame: Any, direction: Any) -> None:
                    await super().process_frame(frame, direction)
                    if isinstance(frame, StartFrame):
                        self.first_audio_event.set()
                        await self.push_frame(frame)
                        prompt = (
                            "SYSTEM_INTERNAL: The user has just connected to the call. "
                            "Introduce yourself exactly as: 'Hello, welcome to LuMay Insurance. I'm the LuMay AI Assistant. How can I help you today?'"
                        )
                        self._generation_task = asyncio.create_task(self._dispatch_turn(prompt))
                    elif isinstance(frame, VADUserStartedSpeakingFrame):
                        # Cancel any pending grace-dispatch — the user is still
                        # (or again) talking, so the previous "stopped speaking"
                        # signal was premature/stale.
                        self._cancel_dispatch_task()
                        if self._agent_speaking:
                            logger.info("voice_pipeline_barge_in_detected")
                            self._cancel_generation()
                            await self.broadcast_interruption()
                        await self.push_frame(frame)
                    elif isinstance(frame, VADUserStoppedSpeakingFrame):
                        import time
                        self._last_vad_stop_at = time.monotonic()
                        self._cancel_dispatch_task()
                        self._dispatch_task = asyncio.create_task(self._grace_then_dispatch(_VAD_GRACE_SECS))
                        await self.push_frame(frame)
                    elif isinstance(frame, TranscriptionFrame):
                        import time
                        self.first_audio_event.set()
                        self._turn_buffer.append(frame.text.strip())
                        self._cancel_dispatch_task()
                        vad_is_fresh = (
                            self._last_vad_stop_at is not None
                            and (time.monotonic() - self._last_vad_stop_at) < _VAD_RECENCY_WINDOW_SECS
                        )
                        grace = _VAD_GRACE_SECS if vad_is_fresh else _FALLBACK_GRACE_SECS
                        self._dispatch_task = asyncio.create_task(self._grace_then_dispatch(grace))
                    elif isinstance(frame, InterimTranscriptionFrame):
                        self._cancel_dispatch_task()
                    elif isinstance(frame, EndFrame) or isinstance(frame, CancelFrame):
                        self._cancel_dispatch_task()
                        self._cancel_generation()
                    elif isinstance(frame, AudioRawFrame):
                        # Discard user audio raw frames to prevent echo loopback to transport.output()
                        pass
                    else:
                        await self.push_frame(frame)

            framework = ConversationFrameworkProcessor(llm_processor)

            logger.info("voice_pipeline_assembling", session_id=self._session_id)
            pipeline = Pipeline([
                transport.input(),
                vad_processor,
                stt_service,
                framework,
                tts_service,
                transport.output(),
            ])

            from pipecat.pipeline.worker import PipelineWorker

            runner = PipelineRunner()
            task = PipelineWorker(pipeline)
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
