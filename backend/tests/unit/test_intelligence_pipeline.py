"""Complaint Intelligence — pipeline unit tests."""

import pytest

from ai.intelligence.pipeline import (
    build_metadata,
    build_prompt,
    parse_json_response,
    preprocess,
    validate_confidence,
)
from ai.prompts.base_prompt import get_prompt_registry, reset_prompt_registry
from ai.prompts.templates import register_default_prompts
from ai.intelligence.prompts import register_complaint_prompts


@pytest.fixture(autouse=True)
def _setup_prompts():
    reset_prompt_registry()
    register_default_prompts()
    register_complaint_prompts()
    yield
    reset_prompt_registry()


class TestPreprocess:
    def test_strips_whitespace(self) -> None:
        result = preprocess("  Hello world  ")
        assert result == "Hello world"

    def test_preserves_content(self) -> None:
        result = preprocess("My insurance claim was denied")
        assert result == "My insurance claim was denied"

    def test_empty_string(self) -> None:
        result = preprocess("")
        assert result == ""


class TestBuildPrompt:
    def test_system_prompt_renders(self) -> None:
        system, user = build_prompt(
            "complaint/classification/system",
            "complaint/classification/user",
            {"complaint_text": "Billing error on my policy"},
        )
        assert "complaint" in system.lower()
        assert "JSON" in system

    def test_user_prompt_contains_text(self) -> None:
        system, user = build_prompt(
            "complaint/classification/system",
            "complaint/classification/user",
            {"complaint_text": "Policy renewal issue"},
        )
        assert "Policy renewal issue" in user

    def test_summary_with_max_words(self) -> None:
        system, user = build_prompt(
            "complaint/summary/system",
            "complaint/summary/user",
            {"complaint_text": "My claim", "max_words": 100},
        )
        assert "100" in system
        assert "My claim" in user


class TestParseJsonResponse:
    def test_clean_json(self) -> None:
        result = parse_json_response('{"label": "test", "confidence": 0.95}')
        assert result is not None
        assert result["label"] == "test"
        assert result["confidence"] == 0.95

    def test_json_with_code_fence(self) -> None:
        result = parse_json_response('```json\n{"label": "test"}\n```')
        assert result is not None
        assert result["label"] == "test"

    def test_json_inside_text(self) -> None:
        result = parse_json_response(
            'Here is the result: {"label": "billing", "confidence": 0.9}'
        )
        assert result is not None
        assert result["label"] == "billing"

    def test_extract_braces(self) -> None:
        result = parse_json_response(
            'Some text before {"key": "value"} some text after'
        )
        assert result is not None
        assert result["key"] == "value"

    def test_invalid_json_returns_none(self) -> None:
        result = parse_json_response("Not JSON at all")
        assert result is None

    def test_empty_string(self) -> None:
        result = parse_json_response("")
        assert result is None


class TestValidateConfidence:
    def test_valid_float(self) -> None:
        assert validate_confidence({"confidence": 0.85}) == 0.85

    def test_clamps_low(self) -> None:
        assert validate_confidence({"confidence": -0.5}) == 0.0

    def test_clamps_high(self) -> None:
        assert validate_confidence({"confidence": 1.5}) == 1.0

    def test_missing_key(self) -> None:
        assert validate_confidence({}) == 0.5

    def test_string_value(self) -> None:
        assert validate_confidence({"confidence": "0.92"}) == 0.92

    def test_invalid_type(self) -> None:
        assert validate_confidence({"confidence": "high"}) == 0.0


class TestBuildMetadata:
    def test_creates_metadata(self) -> None:
        m = build_metadata(
            model_used="gpt-4o",
            processing_time_ms=120.456,
            token_usage={"prompt_tokens": 50, "completion_tokens": 30},
            prompt_name="test/prompt",
            explanation="Test",
        )
        assert m.model_used == "gpt-4o"
        assert m.processing_time_ms == 120.46
        assert m.token_usage["prompt_tokens"] == 50
        assert m.prompt_name == "test/prompt"

    def test_empty_token_usage(self) -> None:
        m = build_metadata("", 0, None, "", "")
        assert m.token_usage == {}