"""AI Provider Adapters — LLM backends behind a common interface.

Each provider implements the BaseLLMProvider contract.
Providers are selected and configured at runtime via settings.
"""

from ai.providers.base import BaseLLMProvider, create_provider
from ai.providers.azure_openai import AzureOpenAIProvider
from ai.providers.local_provider import LocalProvider
from ai.providers.openai_provider import OpenAIProvider

__all__ = [
    "AzureOpenAIProvider",
    "BaseLLMProvider",
    "LocalProvider",
    "OpenAIProvider",
    "create_provider",
]