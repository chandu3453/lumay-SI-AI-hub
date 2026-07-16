from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import APP_DESCRIPTION, APP_NAME, APP_VERSION
from app.config.environment import Environment
from app.config.validators import parse_cors_origins


class ApplicationSettings(BaseModel):
    name: str = Field(default=APP_NAME)
    version: str = Field(default=APP_VERSION)
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    secret_key: SecretStr = Field(default="change-me-to-a-secure-app-secret")
    debug: bool = Field(default=False)


class DatabaseSettings(BaseModel):
    url: str = Field(
        default="postgresql+asyncpg://lumay_user:password@localhost:5432/lumay_si_db"
    )
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    echo: bool = Field(default=False)


class RedisSettings(BaseModel):
    url: str = Field(default="redis://localhost:6379/0")
    max_connections: int = Field(default=50, ge=5)


class RabbitMQSettings(BaseModel):
    url: str = Field(default="amqp://guest:guest@localhost:5672/")


class OpenSearchSettings(BaseModel):
    url: str = Field(default="http://localhost:9200")
    user: str = Field(default="admin")
    password: str = Field(default="admin")
    use_ssl: bool = Field(default=False)


class MinIOSettings(BaseModel):
    endpoint: str = Field(default="localhost:9000")
    access_key: str = Field(default="minioadmin")
    secret_key: str = Field(default="minioadmin")
    secure: bool = Field(default=False)
    default_bucket: str = Field(default="lumay-documents")


class JWTSettings(BaseModel):
    secret_key: SecretStr = Field(default="change-me-to-a-secure-jwt-secret")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)


class AzureOpenAISettings(BaseModel):
    endpoint: str = Field(default="https://your-resource.openai.azure.com/")
    api_key: SecretStr = Field(default="")
    api_version: str = Field(default="2024-02-01")
    deployment_gpt4: str = Field(default="gpt-4o")
    deployment_embedding: str = Field(default="text-embedding-3-large")


class OpenAISettings(BaseModel):
    api_key: SecretStr = Field(default="")
    model: str = Field(default="gpt-4o")
    embedding_model: str = Field(default="text-embedding-3-large")


class LoggingSettings(BaseModel):
    level: str = Field(default="INFO")
    format: Literal["json", "console"] = Field(default="json")


class CorsSettings(BaseModel):
    allowed_origins: list[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])
    allow_credentials: bool = Field(default=True)

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v: str | list[str]) -> list[str]:
        return parse_cors_origins(v)


class ObservabilitySettings(BaseModel):
    otel_enabled: bool = Field(default=False)
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_service_name: str = Field(default="lumay-si-ai-hub")
    otel_environment: str = Field(default="development")


class AISettings(BaseModel):
    default_provider: Literal["azure_openai", "openai", "local"] = Field(
        default="azure_openai"
    )
    default_model: str = Field(default="gpt-4o")
    default_embedding_model: str = Field(default="text-embedding-3-large")
    max_retries: int = Field(default=3, ge=0, le=10)
    request_timeout_seconds: int = Field(default=60, ge=1, le=300)
    max_tokens_default: int = Field(default=4096, ge=64, le=128000)
    temperature_default: float = Field(default=0.0, ge=0.0, le=2.0)
    fallback_provider: str | None = Field(default=None)
    enabled: bool = Field(default=True)


class AIPricingSettings(BaseModel):
    gpt4o_per_1k_prompt: float = Field(default=0.0025)
    gpt4o_per_1k_completion: float = Field(default=0.01)
    gpt4o_mini_per_1k_prompt: float = Field(default=0.00015)
    gpt4o_mini_per_1k_completion: float = Field(default=0.0006)
    embedding_per_1k_tokens: float = Field(default=0.00013)


class LiveKitSettings(BaseModel):
    url: str = Field(default="wss://lumay.livekit.cloud")
    api_key: str = Field(default="")
    api_secret: SecretStr = Field(default="")


class AzureSpeechSettings(BaseModel):
    key: SecretStr = Field(default="")
    region: str = Field(default="eastus")
    stt_endpoint: str | None = Field(default=None)
    tts_endpoint: str | None = Field(default=None)
    default_voice: str = Field(default="en-US-JennyNeural")


class VoiceSettings(BaseModel):
    enabled: bool = Field(default=True)
    pipecat_enabled: bool = Field(default=True)
    max_session_duration_seconds: int = Field(default=3600, ge=60, le=14400)
    turn_detection_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    silence_duration_ms: int = Field(default=800, ge=100, le=5000)
    prefix_padding_ms: int = Field(default=300, ge=0, le=2000)


class KrispSettings(BaseModel):
    enabled: bool = Field(default=False)
    license_key: str = Field(default="")


class FeatureFlags(BaseModel):
    ai_enabled: bool = Field(default=True)
    pii_redaction: bool = Field(default=True)
    sentiment_analysis: bool = Field(default=True)
    audit_log: bool = Field(default=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    application: ApplicationSettings = Field(default_factory=ApplicationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    opensearch: OpenSearchSettings = Field(default_factory=OpenSearchSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    azure_openai: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    ai: AISettings = Field(default_factory=AISettings)
    ai_pricing: AIPricingSettings = Field(default_factory=AIPricingSettings)
    livekit: LiveKitSettings = Field(default_factory=LiveKitSettings)
    azure_speech: AzureSpeechSettings = Field(default_factory=AzureSpeechSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    krisp: KrispSettings = Field(default_factory=KrispSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    @model_validator(mode="after")
    def _validate_production(self) -> "Settings":
        if self.application.environment == Environment.PRODUCTION:
            if self.application.debug:
                raise ValueError("app_debug must be False in production")
            if "change-me" in self.application.secret_key.get_secret_value().lower():
                raise ValueError("application.secret_key must be changed in production")
            if "change-me" in self.jwt.secret_key.get_secret_value().lower():
                raise ValueError("jwt.secret_key must be changed in production")
        return self
