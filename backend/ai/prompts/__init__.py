"""AI Prompts — versioned, tested prompt templates.

Prompts are stored as templates with version metadata.
The PromptRegistry provides lookup by name, version, or tag.
"""

from ai.prompts.base_prompt import BasePrompt, PromptRegistry, PromptVersion, get_prompt_registry, reset_prompt_registry
from ai.prompts.loader import load_prompt_from_dict, load_prompt_from_file, register_prompt, register_prompt_from_file
from ai.prompts.templates import register_default_prompts

__all__ = [
    "BasePrompt",
    "PromptRegistry",
    "PromptVersion",
    "get_prompt_registry",
    "load_prompt_from_dict",
    "load_prompt_from_file",
    "register_default_prompts",
    "register_prompt",
    "register_prompt_from_file",
    "reset_prompt_registry",
]