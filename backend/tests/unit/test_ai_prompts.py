"""AI Platform — prompt management unit tests."""

import pytest

from ai.exceptions import AIPromptNotFoundError, AIPromptError
from ai.prompts.base_prompt import BasePrompt, PromptRegistry, PromptVersion, get_prompt_registry, reset_prompt_registry


class TestPromptVersion:
    def test_parse_simple(self) -> None:
        v = PromptVersion.parse("v1.0.0")
        assert v.major == 1
        assert v.minor == 0
        assert v.revision == 0

    def test_parse_without_v(self) -> None:
        v = PromptVersion.parse("2.3.1")
        assert v.major == 2
        assert v.minor == 3
        assert v.revision == 1

    def test_str_representation(self) -> None:
        v = PromptVersion(2, 1, 0)
        assert str(v) == "v2.1.0"

    def test_default_version(self) -> None:
        prompt = BasePrompt(template="Hello {name}", name="test")
        assert str(prompt.version) == "v1.0.0"


class TestBasePrompt:
    def test_render(self) -> None:
        prompt = BasePrompt(
            template="Hello {name}, your {item} is ready.",
            name="greeting",
            variables={"name": str, "item": str},
        )
        rendered = prompt.render(name="Alice", item="report")
        assert rendered == "Hello Alice, your report is ready."

    def test_render_missing_variable_raises(self) -> None:
        prompt = BasePrompt(
            template="Hello {name}", name="test",
            variables={"name": str},
        )
        with pytest.raises(AIPromptError):
            prompt.render(wrong_key="value")

    def test_to_dict(self) -> None:
        prompt = BasePrompt(template="Test", name="test-prompt", version=PromptVersion(1, 2, 3), description="A test")
        data = prompt.to_dict()
        assert data["name"] == "test-prompt"
        assert data["version"] == "v1.2.3"
        assert data["description"] == "A test"

    def test_variables_property(self) -> None:
        prompt = BasePrompt(template="{a}{b}", name="test", variables={"a": str, "b": int})
        assert prompt.variables == {"a": str, "b": int}
        assert prompt.variables is not prompt._variables  # defensive copy


class TestPromptRegistry:
    def setup_method(self) -> None:
        reset_prompt_registry()

    def test_register_and_get_latest(self) -> None:
        registry = get_prompt_registry()
        v1 = BasePrompt(template="Version 1", name="test", version=PromptVersion(1, 0, 0))
        v2 = BasePrompt(template="Version 2", name="test", version=PromptVersion(2, 0, 0))
        registry.register("test", v1)
        registry.register("test", v2)
        latest = registry.get("test")
        assert latest.template == "Version 2"

    def test_get_specific_version(self) -> None:
        registry = get_prompt_registry()
        v1 = BasePrompt(template="Version 1", name="test", version=PromptVersion(1, 0, 0))
        v2 = BasePrompt(template="Version 2", name="test", version=PromptVersion(2, 0, 0))
        registry.register("test", v1)
        registry.register("test", v2)
        result = registry.get("test", version="1.0.0")
        assert result.template == "Version 1"

    def test_get_nonexistent_raises(self) -> None:
        registry = get_prompt_registry()
        with pytest.raises(AIPromptNotFoundError):
            registry.get("nonexistent")

    def test_get_nonexistent_version_raises(self) -> None:
        registry = get_prompt_registry()
        prompt = BasePrompt(template="Test", name="test", version=PromptVersion(1, 0, 0))
        registry.register("test", prompt)
        with pytest.raises(AIPromptNotFoundError):
            registry.get("test", version="99.0.0")

    def test_register_with_tags(self) -> None:
        registry = get_prompt_registry()
        p1 = BasePrompt(template="Classification", name="classifier", version=PromptVersion(1, 0, 0))
        p2 = BasePrompt(template="Summarization", name="summarizer", version=PromptVersion(1, 0, 0))
        registry.register("classifier", p1, tags=["classification", "system"])
        registry.register("summarizer", p2, tags=["summarization", "system"])
        classified = registry.get_by_tag("classification")
        assert len(classified) == 1
        assert classified[0].name == "classifier"

    def test_list(self) -> None:
        registry = get_prompt_registry()
        p1 = BasePrompt(template="Test1", name="prompt1")
        p2 = BasePrompt(template="Test2", name="prompt2")
        registry.register("prompt1", p1)
        registry.register("prompt2", p2)
        prompts = registry.list()
        assert len(prompts) == 2
        assert all(p["name"] in {"prompt1", "prompt2"} for p in prompts)

    def test_clear(self) -> None:
        registry = get_prompt_registry()
        registry.register("test", BasePrompt(template="Test", name="test"))
        registry.clear()
        with pytest.raises(AIPromptNotFoundError):
            registry.get("test")

    def test_get_by_tag_empty(self) -> None:
        registry = get_prompt_registry()
        result = registry.get_by_tag("nonexistent")
        assert result == []


class TestPromptLoader:
    def test_register_prompt_helper(self) -> None:
        from ai.prompts.loader import register_prompt
        reset_prompt_registry()
        prompt = register_prompt(
            template="Hello {name}",
            name="greeting",
            variables={"name": str},
            description="A greeting",
            tags=["test"],
        )
        assert prompt.name == "greeting"
        registry = get_prompt_registry()
        loaded = registry.get("greeting")
        assert loaded.template == "Hello {name}"

    def test_load_from_dict(self) -> None:
        from ai.prompts.loader import load_prompt_from_dict
        data = {
            "name": "test",
            "template": "Hello {name}",
            "version": {"major": 2, "minor": 0, "revision": 0},
            "variables": {"name": str},
        }
        prompt = load_prompt_from_dict(data)
        assert prompt.name == "test"
        assert str(prompt.version) == "v2.0.0"


class TestDefaultPrompts:
    def test_register_default_prompts(self) -> None:
        from ai.prompts.templates import register_default_prompts
        reset_prompt_registry()
        register_default_prompts()
        registry = get_prompt_registry()
        prompts = registry.list()
        assert len(prompts) == 5
        classification = registry.get("classification/system")
        assert "classification" in classification.template
        summarization = registry.get("summarization/system")
        assert "{max_words}" in summarization.template

    def test_default_prompt_rendering(self) -> None:
        from ai.prompts.templates import register_default_prompts
        reset_prompt_registry()
        register_default_prompts()
        registry = get_prompt_registry()
        user_prompt = registry.get("classification/user")
        rendered = user_prompt.render(text="My insurance claim was denied")
        assert "My insurance claim was denied" in rendered