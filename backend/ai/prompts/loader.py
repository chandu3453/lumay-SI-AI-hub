"""Prompt loader — loads prompt templates from files or inline definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai.prompts.base_prompt import BasePrompt, PromptVersion, get_prompt_registry


def load_prompt_from_dict(data: dict[str, Any]) -> BasePrompt:
    version = PromptVersion(**data["version"]) if isinstance(data.get("version"), dict) else PromptVersion(1, 0, 0)
    variables = data.get("variables", {})
    return BasePrompt(
        template=data["template"],
        version=version,
        variables=variables,
        name=data.get("name", ""),
        description=data.get("description", ""),
    )


def load_prompt_from_file(path: str | Path) -> BasePrompt:
    path = Path(path)
    if path.suffix == ".json":
        with open(path) as f:
            data = json.load(f)
    elif path.suffix == ".txt":
        name = path.stem
        template = path.read_text().strip()
        data = {"name": name, "template": template}
    else:
        raise ValueError(f"Unsupported prompt file format: {path.suffix}")
    return load_prompt_from_dict(data)


def register_prompt_from_file(
    path: str | Path,
    name: str | None = None,
    tags: list[str] | None = None,
) -> BasePrompt:
    prompt = load_prompt_from_file(path)
    if name:
        prompt._name = name
    registry = get_prompt_registry()
    registry.register(prompt.name, prompt, tags=tags)
    return prompt


def register_prompt(
    template: str,
    name: str,
    version: dict | None = None,
    variables: dict[str, type] | None = None,
    description: str = "",
    tags: list[str] | None = None,
) -> BasePrompt:
    pv = PromptVersion(**version) if version else PromptVersion(1, 0, 0)
    prompt = BasePrompt(
        template=template,
        version=pv,
        variables=variables,
        name=name,
        description=description,
    )
    registry = get_prompt_registry()
    registry.register(name, prompt, tags=tags)
    return prompt