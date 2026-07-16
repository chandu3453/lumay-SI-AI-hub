import os
from pathlib import Path
from typing import Literal

from app.config import get_settings
from app.platform.logging import get_logger

# Load .env into os.environ so LIVEKIT_URL, LIVEKIT_API_KEY etc. are available via os.getenv
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(_env_path, override=False)  # override=False: don't overwrite already-set env vars
except ImportError:
    pass  # python-dotenv not installed; env vars must come from OS environment

logger = get_logger(__name__)


def _unwrap_secret(value: object) -> str:
    """Safely get string from SecretStr or plain str."""
    if hasattr(value, "get_secret_value"):
        return value.get_secret_value()  # type: ignore[union-attr]
    return str(value)


class VoiceConfig:
    def __init__(self) -> None:
        settings = get_settings()
        # Read directly from env vars (single underscore format in .env)
        # with fallback to nested settings values
        self.livekit_url: str = os.getenv("LIVEKIT_URL", settings.livekit.url)
        self.livekit_api_key: str = os.getenv("LIVEKIT_API_KEY", settings.livekit.api_key)
        self.livekit_api_secret: str = os.getenv(
            "LIVEKIT_API_SECRET", _unwrap_secret(settings.livekit.api_secret)
        )
        self.stt_provider: Literal["azure", "openai", "deepgram"] = os.getenv("VOICE_STT_PROVIDER", "deepgram")  # type: ignore
        self.tts_provider: Literal["azure", "openai", "elevenlabs", "deepgram"] = os.getenv("VOICE_TTS_PROVIDER", "azure")  # type: ignore
        self.azure_speech_key: str = os.getenv(
            "AZURE_SPEECH_KEY", _unwrap_secret(settings.azure_speech.key)
        )
        self.azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", settings.azure_speech.region)
        self.azure_stt_endpoint: str | None = os.getenv("AZURE_STT_ENDPOINT", settings.azure_speech.stt_endpoint or "") or None
        self.azure_tts_endpoint: str | None = os.getenv("AZURE_TTS_ENDPOINT", settings.azure_speech.tts_endpoint or "") or None
        self.azure_tts_voice: str = os.getenv("AZURE_TTS_VOICE", settings.azure_speech.default_voice)
        self.deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")
        self.max_session_duration: int = int(os.getenv("VOICE_MAX_SESSION_DURATION", str(settings.voice.max_session_duration_seconds)))
        self.pipeline_connect_timeout: int = int(os.getenv("VOICE_CONNECT_TIMEOUT", "60"))
        self.turn_detection_threshold: float = float(os.getenv("REALTIME_TURN_DETECTION_THRESHOLD", str(settings.voice.turn_detection_threshold)))
        self.silence_duration_ms: int = int(os.getenv("REALTIME_SILENCE_DURATION_MS", str(settings.voice.silence_duration_ms)))
        self.prefix_padding_ms: int = int(os.getenv("REALTIME_PREFIX_PADDING_MS", str(settings.voice.prefix_padding_ms)))

    @classmethod
    def from_env(cls) -> "VoiceConfig":
        """Alias for direct instantiation (reads env vars automatically)."""
        return cls()
