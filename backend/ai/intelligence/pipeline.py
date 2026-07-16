"""Complaint Intelligence — pipeline runner.

Each analysis follows the pipeline:
  Input → Preprocessing → Prompt Builder → AI Gateway → Response Parsing → Validation → Output
"""

from __future__ import annotations

import json
import time
from typing import Any

from ai.gateway.ai_gateway import AIGateway
from ai.intelligence.models import AnalysisMetadata
from app.platform.logging import get_logger

logger = get_logger(__name__)


def preprocess(complaint_text: str) -> str:
    cleaned = complaint_text.strip()
    return cleaned


def build_prompt(system_prompt_name: str, user_prompt_name: str, variables: dict[str, Any]) -> tuple[str, str]:
    from ai.prompts.base_prompt import get_prompt_registry
    registry = get_prompt_registry()
    system = registry.get(system_prompt_name).render(**{k: v for k, v in variables.items() if k in registry.get(system_prompt_name).variables})
    user = registry.get(user_prompt_name).render(**{k: v for k, v in variables.items() if k in registry.get(user_prompt_name).variables})
    return system, user


def parse_json_response(content: str) -> dict[str, Any] | None:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        import re
        brace_start = content.find("{")
        brace_end = content.rfind("}")
        if brace_start != -1 and brace_end != -1:
            try:
                return json.loads(content[brace_start : brace_end + 1])
            except json.JSONDecodeError:
                pass
        return None


def validate_confidence(data: dict[str, Any]) -> float:
    raw = data.get("confidence", 0.5)
    try:
        return max(0.0, min(1.0, float(raw)))
    except (ValueError, TypeError):
        return 0.0


def build_metadata(
    model_used: str,
    processing_time_ms: float,
    token_usage: dict[str, int] | None,
    prompt_name: str,
    explanation: str = "",
) -> AnalysisMetadata:
    return AnalysisMetadata(
        model_used=model_used,
        processing_time_ms=round(processing_time_ms, 2),
        token_usage=token_usage or {},
        prompt_name=prompt_name,
        explanation=explanation,
    )


async def run_pipeline(
    gateway: AIGateway,
    system_prompt_name: str,
    user_prompt_name: str,
    variables: dict[str, Any],
) -> tuple[dict[str, Any] | None, AnalysisMetadata]:
    start = time.monotonic()
    system, user = build_prompt(system_prompt_name, user_prompt_name, variables)
    response = await gateway.generate(
        prompt=user,
        system_prompt=system,
    )
    elapsed = (time.monotonic() - start) * 1000
    parsed = parse_json_response(response.content)
    token_usage = {
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0,
    } if response.usage else {}
    metadata = build_metadata(
        model_used=response.model or "",
        processing_time_ms=elapsed,
        token_usage=token_usage,
        prompt_name=system_prompt_name,
    )
    return parsed, metadata