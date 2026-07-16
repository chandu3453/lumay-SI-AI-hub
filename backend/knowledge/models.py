"""Knowledge Service — models for policies, FAQ, products."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PolicyArticle:
    id: str
    title: str
    type: str
    summary: str
    coverage_details: str = ""
    exclusions: str = ""
    claim_process: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FAQEntry:
    id: str
    question: str
    answer: str
    category: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProductInfo:
    id: str
    name: str
    type: str
    description: str = ""
    features: list[str] = field(default_factory=list)
    monthly_premium: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeSearchResult:
    query: str
    results: list[dict[str, Any]]
    total: int
    source: str