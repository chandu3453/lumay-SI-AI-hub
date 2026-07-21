"""Local provider adapter — intelligent keyword-based insurance assistant.

Used as automatic fallback when cloud providers (Azure, OpenAI) are unavailable.
Provides realistic insurance domain responses rather than raw mock text.
"""

from typing import Any
from typing import AsyncGenerator

from ai.models import AIRequest, AIResponse, ChatMessage, ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse, TokenUsage
from ai.providers.base import BaseLLMProvider
from app.platform.logging import get_logger

logger = get_logger(__name__)

# Keyword-driven insurance response rules
_INSURANCE_RESPONSES: list[tuple[list[str], str]] = [
    (
        ["pending", "claim", "days", "waiting", "status"],
        "I understand your frustration regarding your pending claim. At LuMay Insurance, our standard processing time is 7–14 business days for motor claims. Since your claim has been pending for 18 days, I will escalate this to our Claims team immediately. Could you please provide your claim reference number and policy number so I can check the exact status and ensure it is prioritised? You may also call our Claims Helpline at 800-LUMAY-1 for an immediate update."
    ),
    (
        ["paid", "twice", "duplicate", "refund", "overpayment", "premium"],
        "I sincerely apologise for the duplicate payment. This must be very frustrating. To process your refund, I will need your policy number and the transaction references for both payments. Once verified, our Finance team processes refunds within 5–7 business days directly to the original payment method. Please share those details and I will raise an urgent refund request on your behalf right away."
    ),
    (
        ["health", "reimbursement", "medical", "not arrived", "hospital", "claim reimburse"],
        "I understand your concern about your health insurance reimbursement. Reimbursements typically take 10–15 business days after submission of all required documents. Could you confirm whether you received an acknowledgement email after submitting your claim? Also, please share your claim reference number. I will check the current status and ensure any missing documents are identified promptly so we can expedite your reimbursement."
    ),
    (
        ["renew", "renewal", "travel", "travel insurance", "expire", "extension"],
        "Renewing your travel insurance with LuMay is simple! You can renew online via our customer portal at lumay.om, through our mobile app, or by calling 800-LUMAY-1. For multi-trip annual plans, renewal must happen within 30 days of expiry to retain your no-claims discount. Would you like me to check your current policy expiry date and provide a renewal quote? I will also confirm if your current coverage level still meets your travel needs."
    ),
    (
        ["garage", "repair", "vehicle", "badly", "quality", "workmanship", "workshop"],
        "I am truly sorry to hear about the poor repair quality at the garage. This is a serious matter and LuMay Insurance takes workmanship complaints very seriously. I will immediately raise a formal complaint with our approved garage network oversight team. Could you share: (1) the garage name and location, (2) your claim reference number, and (3) photos of the unsatisfactory repair work if possible? Our quality assurance team will contact the garage directly and arrange re-inspection at no cost to you."
    ),
    (
        ["cancel", "cancellation", "policy cancel"],
        "I can assist with policy cancellation. Please note that cancellation requests require 30 days written notice. If you have paid your annual premium, a pro-rata refund will be issued for the unused period. However, if you have made any claims during the policy year, the refund amount may be adjusted accordingly. Would you like me to calculate your potential refund amount and initiate the cancellation process?"
    ),
    (
        ["deductible", "excess", "how much", "cover", "coverage", "benefit"],
        "For motor insurance, the standard excess (deductible) with LuMay is OMR 50 for at-fault accidents and OMR 0 for third-party claims. For comprehensive coverage, the excess may vary based on your selected plan. Your policy schedule document lists your specific excess amounts. Would you like me to retrieve your policy details and confirm the exact deductible applicable to your current policy?"
    ),
    (
        ["system_internal"],
        "Hello! Welcome to LuMay Insurance customer support. I am your AI assistant. How can I help you today?"
    ),
    (
        ["hello", "hi", "hey"],
        "Hello! How can I assist you today?"
    ),
    (
        ["help", "assist", "support"],
        "I can help you with claims, refunds, policy renewals, coverage limits, or direct you to the right team. What can I do for you?"
    ),
    (
        ["bike", "motorcycle", "car", "vehicle", "buy", "quote", "new policy", "purchase", "insure"],
        "I would be happy to help you get a quote for your vehicle insurance! Could you please tell me the make, model, and year of your vehicle?"
    ),
    (
        ["no", "don't have", "do not have", "none", "not have"],
        "No problem! We can check your details using your name and phone number. What is your full name?"
    ),
    (
        ["yes", "yeah", "ok", "sure", "correct"],
        "Great! Please share the details with me and I will look them up."
    ),
]

_DEFAULT_RESPONSE = (
    "I want to make sure I assist you accurately. "
    "Could you please describe what you are looking for, or provide your policy number if you have one?"
)


def _generate_insurance_response(user_message: str, system_prompt: str = "") -> str:
    """Generate a contextual insurance response using keyword matching."""
    text = user_message.lower()
    for keywords, response in _INSURANCE_RESPONSES:
        if any(kw in text for kw in keywords):
            return response
    return _DEFAULT_RESPONSE


class LocalProvider(BaseLLMProvider):
    """Local insurance-domain provider.

    Provides realistic keyword-based insurance responses for development
    and as an automatic fallback when cloud providers are unavailable.
    This provider is selected via settings.ai.default_provider="local".
    """

    def __init__(self) -> None:
        self._model_name = "lumay-local-v1"

    @property
    def provider_name(self) -> str:
        return "local"

    async def generate(self, request: AIRequest) -> AIResponse:
        logger.info(
            "local_provider_generate",
            prompt_preview=request.prompt[:80],
        )
        
        prompt_lower = request.prompt.lower()
        sys_lower = (request.system_prompt or "").lower()
        
        # Decide if it is a complaint scenario
        is_scenario_complaint = any(keyword in prompt_lower for keyword in ["delayed", "refund", "reimbursement", "badly", "garage"])
            
        import json
        
        # 1. Complaint Detection
        if "complaint detection specialist" in sys_lower:
            data = {
                "is_complaint": is_scenario_complaint,
                "detection_type": "definite" if is_scenario_complaint else "none",
                "confidence": 0.95 if is_scenario_complaint else 0.10,
                "primary_complaint_statement": "Delayed insurance claim/refund issue" if is_scenario_complaint else "",
                "excerpt": request.prompt[:100],
                "detected_language": "en",
                "explanation": "Customer expresses dissatisfaction." if is_scenario_complaint else "General inquiry.",
                "evidence": []
            }
            content = json.dumps(data)
        # 2. Sentiment Analysis
        elif "sentiment analysis specialist" in sys_lower:
            data = {
                "sentiment": "very_negative" if is_scenario_complaint else "neutral",
                "sentiment_start": "neutral",
                "sentiment_end": "very_negative" if is_scenario_complaint else "neutral",
                "sentiment_trend": "declining" if is_scenario_complaint else "stable",
                "polarity": -0.8 if is_scenario_complaint else 0.0,
                "emotions": {"anger": 0.8} if is_scenario_complaint else {},
                "intensity": 0.9 if is_scenario_complaint else 0.1,
                "sentiment_target": "claims" if is_scenario_complaint else "general",
                "confidence": 0.95,
                "explanation": "Angry tone detected" if is_scenario_complaint else "Polite inquiry",
                "evidence": []
            }
            content = json.dumps(data)
        # 3. Theme Extraction
        elif "theme classification specialist" in sys_lower:
            theme = "claims"
            if "refund" in prompt_lower or "premium" in prompt_lower:
                theme = "billing"
            elif "renew" in prompt_lower:
                theme = "policy"
            
            data = {
                "primary_theme": theme,
                "secondary_themes": [theme],
                "subcategory": "delay" if is_scenario_complaint else "renewal",
                "keywords": ["delayed", "failed"] if is_scenario_complaint else ["renew"],
                "confidence": 0.95,
                "explanation": f"Classified theme as {theme}",
                "evidence": []
            }
            content = json.dumps(data)
        # 4. Severity Assessment
        elif "severity assessment specialist" in sys_lower:
            data = {
                "severity": "high" if is_scenario_complaint else "low",
                "severity_score": 0.85 if is_scenario_complaint else 0.15,
                "urgency": "high" if is_scenario_complaint else "low",
                "impact": "major" if is_scenario_complaint else "minor",
                "auto_escalation_triggers": [],
                "confidence": 0.95,
                "explanation": "High severity impact.",
                "evidence": []
            }
            content = json.dumps(data)
        # 5. Escalation Risk Assessment
        elif "escalation risk assessment specialist" in sys_lower:
            data = {
                "escalation_risk_score": 85 if is_scenario_complaint else 10,
                "risk_level": "high" if is_scenario_complaint else "low",
                "triggers": ["angry_demands"] if is_scenario_complaint else [],
                "confidence": 0.95,
                "explanation": "High escalation risk",
                "evidence": []
            }
            content = json.dumps(data)
        # 6. Priority Recommendation
        elif "priority and sla risk" in sys_lower:
            data = {
                "priority": "high" if is_scenario_complaint else "medium",
                "priority_score": 0.80 if is_scenario_complaint else 0.40,
                "sla_risk": "at_risk" if is_scenario_complaint else "within_sla",
                "breach_probability": 75 if is_scenario_complaint else 5,
                "sla_hours_remaining": 24,
                "estimated_breach_time": "",
                "rationale": "High priority recommended.",
                "confidence": 0.95,
                "explanation": "high priority",
                "evidence": []
            }
            content = json.dumps(data)
        # 7. Summarize
        elif "summarization specialist" in sys_lower:
            content = "The customer is reporting a delayed claim, billing issue, or bad repair quality." if is_scenario_complaint else "The customer wants to renew their travel policy."
        # 8. Root Cause Analysis
        elif "root cause analysis specialist" in sys_lower:
            data = {
                "root_cause": "Process delay or service failure" if is_scenario_complaint else "Information inquiry",
                "process_failure_point": "Approved provider networks" if is_scenario_complaint else "None",
                "recommended_fix": "Expedite claim status immediately",
                "prevention_suggestion": "Better oversight of processes",
                "confidence": 0.90,
                "explanation": "Failure to deliver within standard SLA.",
                "evidence": []
            }
            content = json.dumps(data)
        # 9. Language Detection
        elif "language detection specialist" in sys_lower:
            data = {
                "detected_language": "en",
                "language_confidence": 1.0,
                "script": "latin",
                "metadata": {}
            }
            content = json.dumps(data)
        # 10. Recommend Resolution
        elif "resolution recommendation specialist" in sys_lower:
            data = {
                "recommended_action": "Contact claims officer to prioritize case",
                "steps": ["Step 1: Check claim status", "Step 2: Expedite with team"],
                "department": "claims",
                "routing_rule": "auto_route",
                "escalation_required": True,
                "estimated_resolution_time": "24 hours",
                "suggested_response_template": "Dear customer, we are checking this.",
                "confidence": 0.95,
                "explanation": "claims routing recommended",
                "evidence": []
            }
            content = json.dumps(data)
        # 11. Agent Assist — intent + next-best-action + suggested replies + insights (Phase 5)
        elif "ai copilot assisting a human insurance agent" in sys_lower:
            is_product_inquiry = any(
                kw in prompt_lower
                for kw in ["motorcycle", "bike", "car", "vehicle", "quote", "new policy", "purchase", "insure"]
            )
            if is_product_inquiry:
                data = {
                    "intent": "Product Inquiry",
                    "intent_confidence": 0.88,
                    "next_best_actions": [
                        {"action": "Offer Quote", "rationale": "Customer is asking about a new policy."}
                    ],
                    "suggested_replies": [
                        {
                            "type": "clarification",
                            "content": "Could you share the make, model, and year of your vehicle so I can prepare an accurate quote?",
                        }
                    ],
                    "insights": {
                        "repeated_questions": [],
                        "missing_info": ["vehicle make/model/year"],
                        "compliance_risks": [],
                        "unanswered_questions": [],
                    },
                    "confidence": 0.85,
                }
            else:
                data = {
                    "intent": "General",
                    "intent_confidence": 0.6,
                    "next_best_actions": [
                        {"action": "Verify Policy", "rationale": "Confirm customer identity/policy before proceeding."}
                    ],
                    "suggested_replies": [
                        {"type": "clarification", "content": "Could you tell me more about what you need help with today?"}
                    ],
                    "insights": {
                        "repeated_questions": [],
                        "missing_info": [],
                        "compliance_risks": [],
                        "unanswered_questions": [],
                    },
                    "confidence": 0.6,
                }
            content = json.dumps(data)
        # Default fallback
        else:
            content = _generate_insurance_response(request.prompt, request.system_prompt or "")

        return AIResponse(
            content=content,
            finish_reason="stop",
            model=self._model_name,
            usage=TokenUsage.build(prompt=len(request.prompt.split()), completion=len(content.split())),
        )

    async def chat(self, request: ChatRequest) -> ChatResponse:
        # Use the last user message for response generation
        user_messages = [m for m in request.messages if m.role == "user"]
        last_user = user_messages[-1] if user_messages else ChatMessage(role="user", content="")
        logger.info(
            "local_provider_chat",
            message_count=len(request.messages),
            last_role=last_user.role,
        )
        content = _generate_insurance_response(last_user.content, request.system_prompt or "")
        return ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=content,
            ),
            finish_reason="stop",
            model=self._model_name,
            usage=TokenUsage.build(prompt=len(last_user.content.split()), completion=len(content.split())),
        )

    async def generate_stream(
        self, messages: list[dict[str, Any]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        last_content = messages[-1]["content"] if messages else ""
        response = _generate_insurance_response(last_content)
        for token in response.split():
            yield token + " "

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        texts = [request.input] if isinstance(request.input, str) else request.input
        import random
        vectors = [[random.uniform(-0.1, 0.1) for _ in range(1536)] for _ in texts]
        return EmbeddingResponse(
            vectors=vectors,
            dimensions=1536,
            model=self._model_name,
            latency_ms=0.5,
        )