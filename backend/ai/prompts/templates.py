"""Built-in prompt templates for the AI platform."""

from ai.prompts.base_prompt import get_prompt_registry
from ai.prompts.loader import register_prompt


_CLASSIFICATION_SYSTEM = """You are an AI classification assistant for an insurance platform.
Classify the following input text into the most appropriate category.
Respond with a JSON object containing "label" (the category name) and "confidence" (a float between 0 and 1)."""

_SUMMARIZATION_SYSTEM = """You are an AI summarization assistant for an insurance platform.
Summarize the following text concisely while preserving all key facts, dates, and entities.
Keep the summary under {max_words} words."""

_CHAT_SYSTEM = """You are a helpful AI assistant for the LuMay SMART Insurance AI Hub platform.
You assist with insurance-related queries professionally and concisely.
Always be empathetic and accurate."""


def register_default_prompts() -> None:
    register_prompt(
        template=_CLASSIFICATION_SYSTEM,
        name="classification/system",
        version={"major": 1, "minor": 0, "revision": 0},
        description="System prompt for classification tasks",
        tags=["classification", "system"],
    )
    register_prompt(
        template=_SUMMARIZATION_SYSTEM,
        name="summarization/system",
        version={"major": 1, "minor": 0, "revision": 0},
        variables={"max_words": int},
        description="System prompt for summarization tasks",
        tags=["summarization", "system"],
    )
    register_prompt(
        template=_CHAT_SYSTEM,
        name="chat/system",
        version={"major": 1, "minor": 0, "revision": 0},
        description="Default system prompt for general chat",
        tags=["chat", "system"],
    )
    register_prompt(
        template="Classify the following text: {text}",
        name="classification/user",
        version={"major": 1, "minor": 0, "revision": 0},
        variables={"text": str},
        description="User prompt template for classification",
        tags=["classification", "user"],
    )
    register_prompt(
        template="Summarize the following text:\n\n{text}",
        name="summarization/user",
        version={"major": 1, "minor": 0, "revision": 0},
        variables={"text": str},
        description="User prompt template for summarization",
        tags=["summarization", "user"],
    )