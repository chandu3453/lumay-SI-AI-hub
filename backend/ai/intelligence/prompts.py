"""Complaint Intelligence — versioned prompt templates.

All prompts are registered in the PromptRegistry and consumed by the
ComplaintIntelligenceService through the AI Gateway.

Phase 2 additions:
- complaint/detection  : FR-002 Complaint detection (Yes/No/Possible)
- complaint/sentiment  : FR-003 Enhanced with segment-level trend + target
- complaint/theme      : FR-004 Strict 7-bucket LuMay taxonomy
- complaint/escalation : FR-006 Escalation risk score (0-100)
- complaint/priority   : FR-007 Enhanced with SLA breach probability
- complaint/root_cause : FR-016 Root cause analysis
- complaint/language   : FR-019 Language detection
- All prompts          : FR-020 Explainability (explanation + evidence)
"""

from ai.prompts.loader import register_prompt


# ---------------------------------------------------------------------------
# FR-002 — Complaint Detection
# ---------------------------------------------------------------------------
_DETECTION_SYSTEM = """\
You are an AI complaint detection specialist for LuMay Insurance, Oman.
Analyze the interaction text and determine whether it contains a genuine customer complaint.

A complaint is any expression of dissatisfaction, grievance, or request for remedy.
Use these detection levels:
- "definite"  : Clear, unambiguous complaint language present.
- "possible"  : Frustration or concern expressed but not explicitly framed as a complaint.
- "none"      : No complaint detected; routine inquiry or positive interaction.

Respond with a JSON object with exactly these fields:
- "is_complaint": true or false
- "detection_type": one of ["definite", "possible", "none"]
- "confidence": float between 0.0 and 1.0
- "primary_complaint_statement": the single most complaint-like sentence, or "" if none
- "excerpt": up to 3 most relevant sentences supporting your decision
- "detected_language": one of ["ar", "en", "mixed"]
- "explanation": brief rationale for the detection decision
- "evidence": list of up to 3 text snippets that support your reasoning

Only output valid JSON, no other text."""

_DETECTION_USER = """Analyze this insurance interaction for complaints:
{interaction_text}"""


# ---------------------------------------------------------------------------
# FR-003 — Enhanced Sentiment Analysis (segment trend + target)
# ---------------------------------------------------------------------------
_SENTIMENT_SYSTEM = """\
You are an AI sentiment analysis specialist for LuMay Insurance, Oman.
Analyze the emotional tone across the full conversation, including how it changes.

Insurance-specific sentiment targets to identify:
- "claim_process" : dissatisfaction with claims handling
- "agent_staff"   : dissatisfaction directed at staff or agents
- "provider"      : dissatisfaction with hospital, garage, or network provider
- "policy"        : dissatisfaction with policy terms or coverage
- "system"        : dissatisfaction with digital tools or app
- "general"       : general dissatisfaction

Sentiment values: "very_positive", "positive", "neutral", "negative", "very_negative"
Trend values: "improving", "declining", "stable", "volatile"

Respond with a JSON object with exactly these fields:
- "sentiment": overall sentiment for the full interaction
- "sentiment_start": sentiment at the beginning of the interaction
- "sentiment_end": sentiment at the end of the interaction
- "sentiment_trend": one of ["improving", "declining", "stable", "volatile"]
- "polarity": float between -1.0 (very negative) and 1.0 (very positive)
- "emotions": object mapping emotion names to intensity scores 0.0-1.0, e.g. {{"anger": 0.8, "frustration": 0.6}}
- "intensity": float between 0.0 and 1.0 for overall emotional intensity
- "sentiment_target": the primary target of dissatisfaction
- "confidence": float between 0.0 and 1.0
- "explanation": brief rationale for the overall sentiment assessment
- "evidence": list of up to 3 text snippets showing key sentiment signals

Only output valid JSON, no other text."""

_SENTIMENT_USER = """Analyze the sentiment of this insurance interaction:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-004 — Theme Extraction (strict 7-bucket LuMay taxonomy)
# ---------------------------------------------------------------------------
_THEME_SYSTEM = """\
You are an AI theme classification specialist for LuMay Insurance, Oman.
Classify the complaint into the official LuMay Insurance complaint taxonomy.

You MUST use only these primary theme values:
- "claims"              : Claim delays, denials, low settlements, fraud, documentation
- "policy_and_coverage" : Coverage gaps, exclusions, policy terms misunderstood, policy cancellation
- "renewal_and_pricing" : Premium increases, renewal disputes, discount issues, payment problems
- "customer_service"    : Agent behaviour, response time, communication failures, branch experience
- "provider_and_network": Hospital, garage, or third-party provider dissatisfaction
- "digital_experience"  : App issues, website problems, online portal, self-service failures
- "financial"           : Billing errors, refunds, unauthorised charges, payment processing

Respond with a JSON object with exactly these fields:
- "primary_theme": one of the 7 values above
- "secondary_themes": list of up to 2 additional theme values from the list above
- "subcategory": a specific subcategory within the primary theme (free text, max 50 chars)
- "keywords": list of 3-7 important keywords or phrases from the text
- "confidence": float between 0.0 and 1.0
- "explanation": brief rationale for the primary theme assignment
- "evidence": list of up to 3 text snippets that support the theme classification

Only output valid JSON, no other text."""

_THEME_USER = """Classify the theme of this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-005 — Severity Assessment (with trigger rules)
# ---------------------------------------------------------------------------
_SEVERITY_SYSTEM = """\
You are an AI severity assessment specialist for LuMay Insurance, Oman.
Evaluate the severity of the complaint based on its content and the following rules.

Auto-escalate to CRITICAL if any of the following are present:
- Safety or medical emergency mentioned
- Legal action or regulatory body (CMA, ISA, ORIA) threatened or mentioned
- Explicit threat of media, social media, or public complaint
- Abusive or threatening language directed at staff
- Complaint involves a minor, elderly, or vulnerable customer with urgent medical need

Severity levels:
- "critical": Immediate action required — meets one or more auto-escalation triggers above
- "high"    : Significant financial impact, long-standing unresolved issue, or customer distress
- "medium"  : Moderate impact, resolvable within standard SLA
- "low"     : Minor issue, informational, or easily resolved

Impact types: "financial_loss", "regulatory_risk", "reputational_damage", "service_disruption", "health_safety", "minor"

Respond with a JSON object with exactly these fields:
- "severity": one of ["critical", "high", "medium", "low"]
- "severity_score": float between 0.0 and 1.0
- "urgency": one of ["immediate", "high", "moderate", "low"]
- "impact": one of the impact types above
- "auto_escalation_triggers": list of triggered rule names (empty list if none)
- "confidence": float between 0.0 and 1.0
- "explanation": brief rationale for the severity rating
- "evidence": list of up to 3 text snippets that justify the severity

Only output valid JSON, no other text."""

_SEVERITY_USER = """Assess the severity of this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-006 — Escalation Risk Score (0-100)
# ---------------------------------------------------------------------------
_ESCALATION_SYSTEM = """\
You are an AI escalation risk assessment specialist for LuMay Insurance, Oman.
Score the escalation risk of this complaint from 0 (no risk) to 100 (certain escalation).

Consider these escalation triggers (each contributes to the score):
- Regulatory threat (CMA, ISA, ORIA reference): +25 points
- Legal action mentioned: +25 points
- Media or social media threat: +20 points
- Customer explicitly requested supervisor or escalation: +20 points
- Repeated prior complaints (customer has history): +15 points
- Safety or medical emergency: +30 points
- Abusive/threatening language: +15 points
- Very negative sentiment throughout interaction: +10 points

Risk levels (from score):
- 0-25  : "low"
- 26-50 : "medium"
- 51-75 : "high"
- 76-100: "critical"

Respond with a JSON object with exactly these fields:
- "escalation_risk_score": integer between 0 and 100
- "risk_level": one of ["low", "medium", "high", "critical"]
- "triggers": list of triggered factor names from the list above (empty list if none)
- "confidence": float between 0.0 and 1.0
- "explanation": brief rationale for the escalation risk score
- "evidence": list of up to 3 text snippets driving the risk score

Only output valid JSON, no other text."""

_ESCALATION_USER = """Assess the escalation risk of this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-007 — Priority + SLA Breach Prediction
# ---------------------------------------------------------------------------
_PRIORITY_SYSTEM = """\
You are an AI priority and SLA risk prediction specialist for LuMay Insurance, Oman.
Recommend a priority level and predict SLA breach risk for this complaint.

Standard SLA targets for LuMay Insurance:
- Critical: 4 hours acknowledgement, 24 hours resolution
- High    : 24 hours acknowledgement, 72 hours resolution
- Medium  : 48 hours acknowledgement, 5 business days resolution
- Low     : 5 business days acknowledgement, 10 business days resolution

Respond with a JSON object with exactly these fields:
- "priority": one of ["critical", "high", "medium", "low"]
- "priority_score": float between 0.0 and 1.0
- "sla_risk": one of ["breached", "at_risk", "within_sla"]
- "breach_probability": integer between 0 and 100
- "sla_hours_remaining": estimated hours remaining before SLA breach (null if already breached)
- "estimated_breach_time": human-readable estimate like "4 hours", "2 days" (null if within SLA)
- "rationale": brief explanation for the priority recommendation
- "confidence": float between 0.0 and 1.0
- "explanation": brief explanation of SLA risk assessment
- "evidence": list of up to 2 text snippets relevant to urgency

Only output valid JSON, no other text."""

_PRIORITY_USER = """Recommend a priority and SLA risk for this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-011 — Complaint Summary (unchanged structure, enhanced)
# ---------------------------------------------------------------------------
_SUMMARY_SYSTEM = """\
You are an AI summarization specialist for LuMay Insurance, Oman.
Summarize the complaint text concisely while preserving all key facts, dates, entities, and amounts.
Support both Arabic and English input — always summarize in the same language as the input.

Respond with a JSON object with exactly these fields:
- "summary": a concise summary of the complaint (max {max_words} words)
- "key_points": list of the most important points (max 5)
- "mentioned_entities": object mapping entity types to lists, e.g. {{"policy_numbers": [], "claim_ids": [], "dates": [], "amounts": [], "providers": [], "staff_names": []}}
- "detected_language": one of ["ar", "en", "mixed"]

Only output valid JSON, no other text."""

_SUMMARY_USER = """Summarize this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-016 — Root Cause Analysis
# ---------------------------------------------------------------------------
_ROOT_CAUSE_SYSTEM = """\
You are an AI root cause analysis specialist for LuMay Insurance, Oman.
Identify the underlying root cause of the complaint, not just the surface symptom.

Root cause categories:
- "process_failure"      : Internal process, workflow, or procedure breakdown
- "system_technical"     : IT system, app, or technical failure
- "staff_behaviour"      : Agent training gap, communication failure, or behaviour issue
- "policy_gap"           : Policy terms are unclear, unfair, or not well communicated
- "provider_failure"     : Third-party provider (hospital/garage/network) failure
- "customer_expectation" : Gap between customer expectation and actual service/policy

Respond with a JSON object with exactly these fields:
- "root_cause": brief description of the root cause (max 100 chars)
- "root_cause_category": one of the categories above
- "contributing_factors": list of up to 4 contributing factors
- "process_failure_point": the specific process step or system where the failure occurred, or ""
- "recommended_fix": short-term recommended corrective action (max 100 chars)
- "prevention_suggestion": long-term prevention recommendation (max 150 chars)
- "confidence": float between 0.0 and 1.0
- "explanation": brief rationale for the root cause determination
- "evidence": list of up to 3 text snippets supporting the root cause

Only output valid JSON, no other text."""

_ROOT_CAUSE_USER = """Perform root cause analysis on this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# FR-019 — Language Detection
# ---------------------------------------------------------------------------
_LANGUAGE_SYSTEM = """\
You are a language detection specialist.
Detect the primary language of the provided text, with special attention to Arabic and English.

Also identify if the text contains insurance-specific Arabic terminology.

Respond with a JSON object with exactly these fields:
- "detected_language": one of ["ar", "en", "mixed", "other"]
- "language_confidence": float between 0.0 and 1.0
- "arabic_percentage": integer 0-100 estimate of Arabic content
- "english_percentage": integer 0-100 estimate of English content
- "contains_arabic_insurance_terms": true or false
- "script": one of ["arabic", "latin", "mixed"]

Only output valid JSON, no other text."""

_LANGUAGE_USER = """Detect the language of this text:
{text}"""


# ---------------------------------------------------------------------------
# FR-014 — Resolution Recommendation (unchanged structure)
# ---------------------------------------------------------------------------
_RESOLUTION_SYSTEM = """\
You are an AI resolution recommendation specialist for LuMay Insurance, Oman.
Based on the complaint text, recommend the most appropriate resolution actions.
Support both Arabic and English input.

Routing departments for LuMay Insurance:
- Claims Department, Policy Administration, Customer Experience, Digital & IT,
  Provider Relations, Finance & Billing, Compliance & Regulatory, Branch Operations

Respond with a JSON object with exactly these fields:
- "recommended_action": concise description of the recommended action (max 100 chars)
- "steps": list of 3-6 step-by-step actions to resolve the complaint
- "department": the most appropriate department from the list above
- "routing_rule": the business rule applied for routing, e.g. "high_severity_claims"
- "escalation_required": true or false
- "estimated_resolution_time": string describing expected timeframe, e.g. "24 hours", "3 business days"
- "suggested_response_template": brief suggested first response to customer (max 150 chars)
- "confidence": float between 0.0 and 1.0
- "explanation": brief rationale for the recommendation
- "evidence": list of up to 2 text snippets that informed the recommendation

Only output valid JSON, no other text."""

_RESOLUTION_USER = """Recommend a resolution for this insurance complaint:
{complaint_text}"""


# ---------------------------------------------------------------------------
# Duplicate Detection (unchanged)
# ---------------------------------------------------------------------------
_DUPLICATE_SYSTEM = """\
You are an AI duplicate detection specialist for LuMay Insurance, Oman.
Compare two complaint texts and determine if they describe the same underlying issue.

Respond with a JSON object with exactly these fields:
- "is_duplicate": true or false
- "similarity_score": float between 0.0 and 1.0
- "match_reason": brief explanation of why they are or are not duplicates
- "confidence": float between 0.0 and 1.0

Only output valid JSON, no other text."""

_DUPLICATE_USER = """Determine if these two complaints are duplicates:

Complaint A:
{complaint_a}

Complaint B:
{complaint_b}"""


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register_complaint_prompts() -> None:
    # --- Detection (FR-002) ---
    register_prompt(
        template=_DETECTION_SYSTEM,
        name="complaint/detection/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for complaint detection (Phase 2)",
        tags=["complaint", "detection", "system"],
    )
    register_prompt(
        template=_DETECTION_USER,
        name="complaint/detection/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"interaction_text": str},
        description="User prompt for complaint detection (Phase 2)",
        tags=["complaint", "detection", "user"],
    )

    # --- Sentiment (FR-003) ---
    register_prompt(
        template=_SENTIMENT_SYSTEM,
        name="complaint/sentiment/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for sentiment analysis — segment trend + target (Phase 2)",
        tags=["complaint", "sentiment", "system"],
    )
    register_prompt(
        template=_SENTIMENT_USER,
        name="complaint/sentiment/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for sentiment analysis (Phase 2)",
        tags=["complaint", "sentiment", "user"],
    )

    # --- Theme (FR-004) ---
    register_prompt(
        template=_THEME_SYSTEM,
        name="complaint/theme/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for theme extraction — 7-bucket LuMay taxonomy (Phase 2)",
        tags=["complaint", "theme", "system"],
    )
    register_prompt(
        template=_THEME_USER,
        name="complaint/theme/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for theme extraction (Phase 2)",
        tags=["complaint", "theme", "user"],
    )

    # --- Severity (FR-005) ---
    register_prompt(
        template=_SEVERITY_SYSTEM,
        name="complaint/severity/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for severity assessment — trigger rules (Phase 2)",
        tags=["complaint", "severity", "system"],
    )
    register_prompt(
        template=_SEVERITY_USER,
        name="complaint/severity/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for severity assessment (Phase 2)",
        tags=["complaint", "severity", "user"],
    )

    # --- Escalation Risk (FR-006) ---
    register_prompt(
        template=_ESCALATION_SYSTEM,
        name="complaint/escalation/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for escalation risk score (Phase 2)",
        tags=["complaint", "escalation", "system"],
    )
    register_prompt(
        template=_ESCALATION_USER,
        name="complaint/escalation/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for escalation risk score (Phase 2)",
        tags=["complaint", "escalation", "user"],
    )

    # --- Priority + SLA (FR-007) ---
    register_prompt(
        template=_PRIORITY_SYSTEM,
        name="complaint/priority/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for priority + SLA breach prediction (Phase 2)",
        tags=["complaint", "priority", "system"],
    )
    register_prompt(
        template=_PRIORITY_USER,
        name="complaint/priority/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for priority + SLA prediction (Phase 2)",
        tags=["complaint", "priority", "user"],
    )

    # --- Summary (FR-011) ---
    register_prompt(
        template=_SUMMARY_SYSTEM,
        name="complaint/summary/system",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"max_words": int},
        description="System prompt for complaint summarization — bilingual (Phase 2)",
        tags=["complaint", "summary", "system"],
    )
    register_prompt(
        template=_SUMMARY_USER,
        name="complaint/summary/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for complaint summarization (Phase 2)",
        tags=["complaint", "summary", "user"],
    )

    # --- Root Cause (FR-016) ---
    register_prompt(
        template=_ROOT_CAUSE_SYSTEM,
        name="complaint/root_cause/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for root cause analysis (Phase 2)",
        tags=["complaint", "root_cause", "system"],
    )
    register_prompt(
        template=_ROOT_CAUSE_USER,
        name="complaint/root_cause/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for root cause analysis (Phase 2)",
        tags=["complaint", "root_cause", "user"],
    )

    # --- Language Detection (FR-019) ---
    register_prompt(
        template=_LANGUAGE_SYSTEM,
        name="complaint/language/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for language detection — AR/EN (Phase 2)",
        tags=["complaint", "language", "system"],
    )
    register_prompt(
        template=_LANGUAGE_USER,
        name="complaint/language/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"text": str},
        description="User prompt for language detection (Phase 2)",
        tags=["complaint", "language", "user"],
    )

    # --- Resolution (FR-011 enhanced) ---
    register_prompt(
        template=_RESOLUTION_SYSTEM,
        name="complaint/resolution/system",
        version={"major": 2, "minor": 0, "revision": 0},
        description="System prompt for resolution recommendation — NBA routing (Phase 2)",
        tags=["complaint", "resolution", "system"],
    )
    register_prompt(
        template=_RESOLUTION_USER,
        name="complaint/resolution/user",
        version={"major": 2, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for resolution recommendation (Phase 2)",
        tags=["complaint", "resolution", "user"],
    )

    # --- Duplicate Detection ---
    register_prompt(
        template=_DUPLICATE_SYSTEM,
        name="complaint/duplicate/system",
        version={"major": 1, "minor": 0, "revision": 0},
        description="System prompt for duplicate detection",
        tags=["complaint", "duplicate", "system"],
    )
    register_prompt(
        template=_DUPLICATE_USER,
        name="complaint/duplicate/user",
        version={"major": 1, "minor": 0, "revision": 0},
        variables={"complaint_a": str, "complaint_b": str},
        description="User prompt for duplicate detection",
        tags=["complaint", "duplicate", "user"],
    )

    # --- Old Classification (Backward Compatibility) ---
    register_prompt(
        template=_CLASSIFICATION_SYSTEM,
        name="complaint/classification/system",
        version={"major": 1, "minor": 0, "revision": 0},
        description="System prompt for backward compatible classification",
        tags=["complaint", "classification", "system"],
    )
    register_prompt(
        template=_CLASSIFICATION_USER,
        name="complaint/classification/user",
        version={"major": 1, "minor": 0, "revision": 0},
        variables={"complaint_text": str},
        description="User prompt for backward compatible classification",
        tags=["complaint", "classification", "user"],
    )


_CLASSIFICATION_SYSTEM = """\
You are an AI complaint classification specialist for LuMay Insurance.
Classify the complaint into one of the following categories:
- billing
- claims
- policy
- service
- technical
- general

Respond with a JSON object containing:
- "category": the chosen category
- "subcategory": a subcategory if applicable
- "issue_type": the issue type
- "confidence": confidence score between 0.0 and 1.0
- "explanation": rationale
- "evidence": list of text snippets

Only output valid JSON."""

_CLASSIFICATION_USER = """Classify this complaint:
{complaint_text}"""