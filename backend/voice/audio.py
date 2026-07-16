"""Audio provider abstraction layer for STT and TTS.

Supports config-driven provider selection:
    STT: Azure Speech, OpenAI Realtime, Deepgram
    TTS: Azure Speech, OpenAI, ElevenLabs
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Literal

from app.platform.logging import get_logger

logger = get_logger(__name__)


# ── STT Provider Abstraction ──────────────────────────────────────

class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        ...

    @abstractmethod
    async def transcribe_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[dict[str, str | bool], None]:
        ...


class AzureSTTProvider(STTProvider):
    def __init__(self, key: str, region: str, endpoint: str | None = None) -> None:
        self._key = key
        self._region = region
        self._endpoint = endpoint

    async def transcribe(self, audio_data: bytes) -> str:
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_config = speechsdk.SpeechConfig(
                subscription=self._key,
                region=self._region,
            )
            if self._endpoint:
                speech_config.endpoint_id = self._endpoint

            push_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
            )

            push_stream.write(audio_data)
            push_stream.close()

            result = recognizer.recognize_once()
            return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else ""
        except ImportError:
            logger.warning("azure_speech_sdk_not_installed_falling_back")
            return ""
        except Exception as exc:
            logger.error("azure_stt_failed", error=str(exc))
            return ""

    async def transcribe_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[dict[str, str | bool], None]:
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_config = speechsdk.SpeechConfig(
                subscription=self._key,
                region=self._region,
            )
            if self._endpoint:
                speech_config.endpoint_id = self._endpoint

            push_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
            )

            recognizer.recognizing.connect(
                lambda evt: self._push_interim(evt)
            )

            async for chunk in audio_stream:
                push_stream.write(chunk)

            push_stream.close()
            result = recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                yield {"text": result.text, "is_partial": False}
        except ImportError:
            logger.warning("azure_speech_sdk_not_installed_falling_back")
        except Exception as exc:
            logger.error("azure_stt_stream_failed", error=str(exc))

    def _push_interim(self, evt: object) -> None:
        pass


class OpenAIRealtimeSTTProvider(STTProvider):
    def __init__(self, api_key: str, model: str = "whisper-1") -> None:
        self._api_key = api_key
        self._model = model

    async def transcribe(self, audio_data: bytes) -> str:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key)
            import io

            buffer = io.BytesIO(audio_data)
            buffer.name = "audio.wav"
            transcript = await client.audio.transcriptions.create(
                model=self._model,
                file=buffer,
            )
            return transcript.text or ""
        except Exception as exc:
            logger.error("openai_stt_failed", error=str(exc))
            return ""

    async def transcribe_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[dict[str, str | bool], None]:
        chunks = []
        async for chunk in audio_stream:
            chunks.append(chunk)
        full_audio = b"".join(chunks)
        text = await self.transcribe(full_audio)
        if text:
            yield {"text": text, "is_partial": False}


class DeepgramSTTProvider(STTProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def transcribe(self, audio_data: bytes) -> str:
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    headers={
                        "Authorization": f"Token {self._api_key}",
                        "Content-Type": "audio/wav",
                    },
                    content=audio_data,
                    params={"model": "nova-2", "smart_format": "true"},
                )
                data = response.json()
                return (
                    data.get("results", {})
                    .get("channels", [{}])[0]
                    .get("alternatives", [{}])[0]
                    .get("transcript", "")
                )
        except Exception as exc:
            logger.error("deepgram_stt_failed", error=str(exc))
            return ""

    async def transcribe_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[dict[str, str | bool], None]:
        import json
        import httpx

        chunks = []
        async for chunk in audio_stream:
            chunks.append(chunk)
        full_audio = b"".join(chunks)
        text = await self.transcribe(full_audio)

        interim_chars = ""
        for char in text:
            interim_chars += char
            yield {"text": interim_chars, "is_partial": True}

        if text:
            yield {"text": text, "is_partial": False}


def create_stt_provider(
    provider: Literal["azure", "openai", "deepgram"] | None = None,
) -> STTProvider:
    from voice.config import VoiceConfig

    cfg = VoiceConfig()
    provider = provider or cfg.stt_provider

    if provider == "azure":
        return AzureSTTProvider(
            key=cfg.azure_speech_key,
            region=cfg.azure_speech_region,
            endpoint=cfg.azure_stt_endpoint,
        )
    elif provider == "openai":
        from app.config import get_settings

        settings = get_settings()
        return OpenAIRealtimeSTTProvider(
            api_key=settings.openai.api_key.get_secret_value(),
        )
    elif provider == "deepgram":
        import os
        api_key = os.getenv("DEEPGRAM_API_KEY", cfg.deepgram_api_key)
        return DeepgramSTTProvider(api_key=api_key)
    else:
        logger.warning("unknown_stt_provider_falling_back_to_azure", provider=provider)
        return AzureSTTProvider(
            key=cfg.azure_speech_key,
            region=cfg.azure_speech_region,
            endpoint=cfg.azure_stt_endpoint,
        )


# ── TTS Provider Abstraction ──────────────────────────────────────

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        ...

    @abstractmethod
    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        ...


class AzureTTSProvider(TTSProvider):
    def __init__(self, key: str, region: str, voice: str, endpoint: str | None = None) -> None:
        self._key = key
        self._region = region
        self._voice = voice
        self._endpoint = endpoint

    async def synthesize(self, text: str) -> bytes:
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_config = speechsdk.SpeechConfig(
                subscription=self._key,
                region=self._region,
            )
            if self._endpoint:
                speech_config.endpoint_id = self._endpoint

            speech_config.speech_synthesis_voice_name = self._voice
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            result = synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            return b""
        except ImportError:
            logger.warning("azure_speech_sdk_not_installed_falling_back")
            return b""
        except Exception as exc:
            logger.error("azure_tts_failed", error=str(exc))
            return b""

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        audio = await self.synthesize(text)
        if audio:
            yield audio


class OpenAITTSProvider(TTSProvider):
    def __init__(self, api_key: str, voice: str = "alloy", model: str = "tts-1") -> None:
        self._api_key = api_key
        self._voice = voice
        self._model = model

    async def synthesize(self, text: str) -> bytes:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key)
            response = await client.audio.speech.create(
                model=self._model,
                voice=self._voice,
                input=text,
            )
            return response.content
        except Exception as exc:
            logger.error("openai_tts_failed", error=str(exc))
            return b""

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        audio = await self.synthesize(text)
        if audio:
            yield audio


class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> None:
        self._api_key = api_key
        self._voice_id = voice_id

    async def synthesize(self, text: str) -> bytes:
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{self._voice_id}",
                    headers={
                        "xi-api-key": self._api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.5,
                        },
                    },
                )
                return response.content
        except Exception as exc:
            logger.error("elevenlabs_tts_failed", error=str(exc))
            return b""

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        audio = await self.synthesize(text)
        if audio:
            yield audio


class DeepgramTTSProvider(TTSProvider):
    def __init__(self, api_key: str, voice: str = "aura-asteria-en") -> None:
        self._key = api_key
        self._voice = voice

    async def synthesize(self, text: str) -> bytes:
        return b""

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        yield b""


def create_tts_provider(
    provider: Literal["azure", "openai", "elevenlabs", "deepgram"] | None = None,
) -> TTSProvider:
    from voice.config import VoiceConfig

    cfg = VoiceConfig()
    provider = provider or cfg.tts_provider

    if provider == "azure":
        return AzureTTSProvider(
            key=cfg.azure_speech_key,
            region=cfg.azure_speech_region,
            voice=cfg.azure_tts_voice,
            endpoint=cfg.azure_tts_endpoint,
        )
    elif provider == "openai":
        from app.config import get_settings

        settings = get_settings()
        return OpenAITTSProvider(
            api_key=settings.openai.api_key.get_secret_value(),
        )
    elif provider == "elevenlabs":
        import os
        api_key = os.getenv("ELEVENLABS_API_KEY", "")
        return ElevenLabsTTSProvider(api_key=api_key)
    elif provider == "deepgram":
        import os
        api_key = os.getenv("DEEPGRAM_API_KEY", cfg.deepgram_api_key)
        return DeepgramTTSProvider(api_key=api_key)
    else:
        logger.warning("unknown_tts_provider_falling_back_to_azure", provider=provider)
        return AzureTTSProvider(
            key=cfg.azure_speech_key,
            region=cfg.azure_speech_region,
            voice=cfg.azure_tts_voice,
            endpoint=cfg.azure_tts_endpoint,
        )
