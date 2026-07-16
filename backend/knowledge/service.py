"""Knowledge Service — retrieval for policies, FAQ, products."""

from __future__ import annotations

from typing import Any

from ai.gateway.ai_gateway import AIGateway, get_ai_gateway
from knowledge.models import KnowledgeSearchResult
from knowledge.repository import get_knowledge_repository
from app.platform.logging import get_logger

logger = get_logger(__name__)

_RAG_SYSTEM_PROMPT = """You are a helpful insurance knowledge assistant for the LuMay SMART Insurance AI Hub.
Answer the customer's question using ONLY the provided context.
If the context does not contain enough information, say so honestly.
Always cite your sources (policy ID, FAQ ID, or product name).
Be concise, accurate, and professional."""

_RAG_USER_TEMPLATE = """Context:
{context}

Question: {question}

Answer the question based only on the provided context."""


class KnowledgeService:
    def __init__(self, gateway: AIGateway | None = None) -> None:
        self._gateway = gateway or get_ai_gateway()
        self._repo = get_knowledge_repository()

    def search(self, query: str, source: str | None = None) -> KnowledgeSearchResult:
        if source == "policy":
            results = self._repo.search_policies(query)
            source_label = "policy"
        elif source == "faq":
            results = self._repo.search_faq(query)
            source_label = "faq"
        elif source == "product":
            results = self._repo.search_products(query)
            source_label = "product"
        else:
            results = self._repo.search_all(query)
            source_label = "all"
        return KnowledgeSearchResult(
            query=query,
            results=results,
            total=len(results),
            source=source_label,
        )

    def get_policy(self, policy_id: str) -> dict[str, Any] | None:
        return self._repo.get_policy(policy_id)

    def get_faq(self, faq_id: str) -> dict[str, Any] | None:
        return self._repo.get_faq(faq_id)

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        return self._repo.get_product(product_id)

    def get_all_policies(self) -> list[dict[str, Any]]:
        return self._repo.policies

    def get_all_faq(self) -> list[dict[str, Any]]:
        return self._repo.faq

    def get_all_products(self) -> list[dict[str, Any]]:
        return self._repo.products

    async def answer_question(self, question: str) -> dict[str, Any]:
        search_result = self.search(question)
        context_parts = []
        sources = []
        for r in search_result.results[:5]:
            if r["source"] == "faq":
                context_parts.append(f"Q: {r['question']}\nA: {r['answer']}")
                sources.append(r["id"])
            elif r["source"] == "policy":
                context_parts.append(f"Policy: {r['title']}\n{r['summary']}")
                sources.append(r["id"])
            elif r["source"] == "product":
                context_parts.append(f"Product: {r['name']}\n{r['description']}")
                sources.append(r["id"])

        context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
        user_prompt = _RAG_USER_TEMPLATE.format(context=context, question=question)

        response = await self._gateway.generate(
            prompt=user_prompt,
            system_prompt=_RAG_SYSTEM_PROMPT,
        )

        return {
            "question": question,
            "answer": response.content,
            "sources": sources,
            "context_used": len(context_parts) > 0,
            "model_used": response.model,
            "token_usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            } if response.usage else {},
        }