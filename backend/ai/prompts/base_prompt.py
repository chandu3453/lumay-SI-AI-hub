"""Base prompt template — abstract foundation for all prompt templates.

Prompts are versioned, typed templates rendered at runtime
with variable substitution and serialisation support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PromptVersion:
    major: int
    minor: int
    revision: int

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.revision}"

    @classmethod
    def parse(cls, version_str: str) -> PromptVersion:
        parts = version_str.strip("v").split(".")
        major, minor, revision = (int(p) for p in parts)
        return cls(major=major, minor=minor, revision=revision)


class BasePrompt:
    def __init__(
        self,
        template: str,
        version: PromptVersion | None = None,
        variables: dict[str, type] | None = None,
        name: str = "",
        description: str = "",
    ) -> None:
        self._template = template
        self._version = version or PromptVersion(1, 0, 0)
        self._variables = variables or {}
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> PromptVersion:
        return self._version

    @property
    def template(self) -> str:
        return self._template

    @property
    def variables(self) -> dict[str, type]:
        return dict(self._variables)

    def render(self, **kwargs: Any) -> str:
        missing = set(self._variables) - set(kwargs)
        if missing:
            from ai.exceptions import AIPromptError
            raise AIPromptError(
                message=f"Missing required prompt variables: {missing}",
                context={"template": self._name, "missing": list(missing)},
            )
        return self._template.format(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "version": str(self._version),
            "description": self._description,
            "template": self._template,
            "variables": {k: v.__name__ for k, v in self._variables.items()},
        }


class PromptRegistry:
    def __init__(self) -> None:
        self._prompts: dict[str, list[tuple[PromptVersion, BasePrompt]]] = {}
        self._tags: dict[str, list[str]] = {}

    def register(self, name: str, prompt: BasePrompt, tags: list[str] | None = None) -> None:
        if name not in self._prompts:
            self._prompts[name] = []
        self._prompts[name].append((prompt.version, prompt))
        self._prompts[name].sort(key=lambda x: (x[0].major, x[0].minor, x[0].revision))
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = []
                if name not in self._tags[tag]:
                    self._tags[tag].append(name)

    def get(self, name: str, version: str | None = None) -> BasePrompt:
        if name not in self._prompts:
            from ai.exceptions import AIPromptNotFoundError
            raise AIPromptNotFoundError(
                message=f"Prompt '{name}' not found in registry.",
                context={"name": name},
            )
        versions = self._prompts[name]
        if version is None:
            return versions[-1][1]
        target = PromptVersion.parse(version)
        for v, prompt in versions:
            if v == target:
                return prompt
        from ai.exceptions import AIPromptNotFoundError
        raise AIPromptNotFoundError(
            message=f"Prompt '{name}' version '{version}' not found.",
            context={"name": name, "version": version, "available": [str(v) for v, _ in versions]},
        )

    def get_by_tag(self, tag: str) -> list[BasePrompt]:
        names = self._tags.get(tag, [])
        result = []
        for name in names:
            try:
                result.append(self.get(name))
            except Exception:
                continue
        return result

    def list(self) -> list[dict[str, Any]]:
        result = []
        for name, versions in self._prompts.items():
            latest = versions[-1][1]
            result.append(latest.to_dict())
        return result

    def clear(self) -> None:
        self._prompts.clear()
        self._tags.clear()


_registry: PromptRegistry | None = None


def get_prompt_registry() -> PromptRegistry:
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry


def reset_prompt_registry() -> None:
    global _registry
    _registry = None