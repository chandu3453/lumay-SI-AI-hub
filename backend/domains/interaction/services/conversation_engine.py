import uuid
import json
import asyncio
from datetime import datetime, timezone
from dataclasses import asdict

from app.platform.logging import get_logger
from app.demo.synthetic import get_synthetic_store
from domains.interaction.constants.interaction_constants import InteractionChannel, InteractionDirection, InteractionStatus
from domains.interaction.schemas.interaction_schemas import ChatMessageResponse
from domains.complaint.schemas.complaint_schemas import ComplaintCreate
from domains.workflow.schemas.workflow_schemas import WorkflowCreate
from domains.notification.schemas.notification_schemas import NotificationCreate
from domains.notification.constants.notification_constants import NotificationType, NotificationChannel
from ai.gateway.ai_gateway import get_ai_gateway
from ai.models import ChatMessage
from ai.intelligence.service import ComplaintIntelligenceService
from knowledge.service import KnowledgeService

logger = get_logger(__name__)

_CONVERSATION_STATES: dict[uuid.UUID, dict] = {}

_INTENT_ANALYZER_PROMPT = """Analyze the conversation history and the user's latest message.
Update the conversation state and memory for the LuMay Insurance AI Platform.

The supported intents are:
- "Product Inquiry" (inquiring about coverage, benefits, details of policies)
- "New Policy Purchase" (wants to buy a new policy or get a new insurance quote)
- "Policy Renewal" (wants to renew an existing policy)
- "Claims" (inquiring about claim status, filing a claim, or claim actions)
- "Complaint" (expressing dissatisfaction, billing issues, delays)
- "Payments" (questions about premium payments, payment methods)
- "Refund" (requesting a refund)
- "Policy Servicing" (changing details on a policy, cancellation)
- "Quote Request" (specifically asking for a price/quote)
- "Coverage Inquiry" (asking what is covered under a policy)
- "Greeting" (hello, hi, standard opening)
- "Small Talk" (how are you, who are you, chitchat)
- "Human Agent Request" (asking for transfer to a human)
- "Unknown" (ambiguous, low confidence)

You must return a valid JSON object matching the following structure:
{
  "intent": "The active intent (e.g. New Policy Purchase). Keep the current intent unless the user explicitly switches topics.",
  "flow_stage": "The current stage in the guided flow.",
  "collected_info": {
    "key": "value"
  },
  "missing_info": [
    "item1", "item2"
  ],
  "customer_preferences": {
    "key": "value"
  },
  "clarification_needed": false,
  "escalate_to_human": false
}

Rules for collected_info/missing_info:
- For "New Policy Purchase": we need vehicle/property/person details, insurance type, coverage type, documents.
- For "Claims": we need claim number, verification info.
- For "Renewal": we need policy number, verification info.
- For "Complaint": we need complaint type, policy number, issue details.
- Always retain previously collected details. Only append new ones.
"""

_BASE_SYSTEM_PROMPT = """You are the official AI assistant representing LuMay Insurance, Oman.
Your goal is to assist customers professionally and empathetically as a consultative Enterprise Insurance Advisor.

PERSONALITY & GREETING:
- You must introduce yourself exactly as: "Hello, welcome to LuMay Insurance. I'm the LuMay AI Assistant."
- NEVER output placeholder text like "[Your Name]" or ask the customer to fill in bracketed values.
- Speak naturally, using short sentences, conversational language, and proper punctuation.
- Strictly avoid Markdown symbols (like **bolding** or bullet lists) in your replies, so the speech synthesis sounds natural. Speak in continuous sentences.
- You must ask exactly one question at a time to guide the flow naturally.

BUSINESS RULES:
1. NO HALLUCINATION: Never invent policy details, dates, or prices. If you don't know, suggest checking or human handover.
2. PREVENT REPETITIVE QUESTIONING: Look at the collected information in the state context. NEVER ask for information the customer has already provided.
3. TURN TAKING: If the customer begins a sentence with words like "But...", "Actually...", "Wait...", or "I mean...", yield and let them speak, keeping responses patient and helpful.
4. CLARIFICATION HANDLING: If the customer's intent is ambiguous or if STT confidence is low, ask a clear clarifying question (e.g. "Did you mean motorcycle insurance?") instead of assuming the wrong intent.
5. SMART HANDOVER: Only transfer to a human agent when explicitly requested, after multiple failed clarification attempts, or when policy rules strictly require manual intervention.
"""

_PROMPT_NEW_POLICY_PURCHASE = """
[INTENT: NEW POLICY PURCHASE]
Act as an experienced, consultative Insurance Sales Advisor.

FLOW STEPS:
1. Identify required insurance type (motorcycle, auto, home, travel).
2. Gather details (vehicle, property, or person details).
3. Assess eligibility and check required documents.
4. Offer a quote based on details.
5. Provide purchase guidance.

STRICT SALES CONSTRAINTS:
- If the customer indicates they want to purchase or get a quote for motorcycle/bike insurance, and you have not yet collected the motorcycle details (e.g., whether it is new or existing, make, model, year), you MUST respond EXACTLY with:
  "Absolutely, I'd be happy to help. Before we prepare the right motorcycle insurance plan, may I know if this is for a new motorcycle or an existing one?"
- Collect information gradually, asking exactly one question at a time. Never ask multiple questions.
"""

_PROMPT_PRODUCT_INQUIRY = """
[INTENT: PRODUCT INQUIRY]
Explain LuMay's insurance products using ONLY the provided Knowledge Base context.
Guide the user through the following stages:
1. Insurance Category
2. Product Explanation
3. Coverage Options
4. Benefits & Eligibility
5. Quote Offer

At the end of your explanation, offer clear guided choices:
"I can also help you: get a quote, compare plans, understand premium costs, or check required documents. Which would you like to do next?"
"""

_PROMPT_CLAIMS = """
[INTENT: CLAIMS]
Guide the customer through the Claims flow:
1. Ask for the Claim Number.
2. Perform customer verification.
3. Check and explain the current Claim Status.
4. Outline any required customer actions (e.g., uploading accident reports).
5. Explain the resolution or next steps.
"""

_PROMPT_COMPLAINT = """
[INTENT: COMPLAINT]
Help the customer log a complaint with maximum empathy:
1. Identify the complaint type and issue.
2. Confirm the policy number or claim ID.
3. Reassure the customer that the complaint will be triaged and solved.
"""

_PROMPT_RENEWAL = """
[INTENT: POLICY RENEWAL]
Guide the customer through the Policy Renewal flow:
1. Verify the current policy number and customer identity.
2. Present renewal options (comprehensive vs third-party liability).
3. Outline premium costs and confirm payment.
"""

def get_message_history(interaction) -> list[dict]:
    if not interaction.transcript:
        return []
    try:
        return json.loads(interaction.transcript)
    except json.JSONDecodeError:
        return [{
            "role": "user",
            "content": interaction.transcript,
            "timestamp": interaction.created_at.isoformat() if interaction.created_at else datetime.now(timezone.utc).isoformat()
        }]

def _not_found_response() -> dict:
    return {
        "answer": "I apologise, but I am unable to process your message right now.",
        "messages": [],
        "ai_analysis": {},
        "context_used": False,
        "auto_triaged": False,
        "complaint_id": None,
        "workflow_id": None,
        "provider_used": "none",
    }


async def _prepare_turn(
    interaction_id: uuid.UUID,
    message: str,
    interaction_service,
    complaint_service,
    workflow_service,
):
    """Shared setup for a conversation turn: loads/updates history, retrieves
    customer + knowledge-base context, runs intent-state analysis, and builds
    the final system prompt + chat message list. Used by both the blocking
    and streaming response-generation paths so that logic isn't duplicated.

    Returns None if the interaction can't be found.
    """
    import time

    interaction = await interaction_service.get_interaction(interaction_id)
    if not interaction:
        logger.error("process_conversation_interaction_not_found", interaction_id=str(interaction_id))
        return None
    history = get_message_history(interaction)

    # Append the new user message
    now_str = datetime.now(timezone.utc).isoformat()
    history.append({
        "role": "user",
        "content": message,
        "timestamp": now_str
    })

    from domains.conversation import integration_hooks as conversation_hooks

    await conversation_hooks.on_message(
        interaction_service._repository._session,
        interaction.id,
        "user",
        interaction.channel,
        message,
    )

    # 2. Retrieve Customer & policy details & previous complaints & workflow history
    customer_repository = complaint_service._customer_repository
    customer = None
    context_str = ""

    if interaction.customer_ref:
        try:
            cust_uuid = uuid.UUID(interaction.customer_ref)
            customer = await customer_repository.get_by_id(cust_uuid)
        except ValueError:
            customer = await customer_repository.get_by_external_ref(interaction.customer_ref)
            if not customer:
                customer = await customer_repository.get_by_email(interaction.customer_ref)

    if customer:
        context_str += f"\nCustomer Name: {customer.full_name}\nCustomer Segment: {customer.segment}\nCustomer Email: {customer.email or 'N/A'}"
        meta = customer.profile_metadata or {}
        policy_num = meta.get("policy_number") or meta.get("policyNumber") or "POL-99281-22"
        product = meta.get("product") or "Motor Comprehensive"
        context_str += f"\nActive Policy: {policy_num} ({product})"

        # Previous complaints
        previous_complaints = await complaint_service._repository.get_by_customer_id(customer.id)
        if previous_complaints:
            context_str += f"\nPrevious Complaints ({len(previous_complaints)}):"
            for pc in previous_complaints[:3]:
                context_str += f"\n- Complaint {pc.complaint_number}: {pc.title} (Status: {pc.status}, Severity: {pc.severity})"

            # Workflow history
            previous_workflows = []
            for comp in previous_complaints[:3]:
                wf = await workflow_service._repository.get_active_by_complaint_id(comp.id)
                if wf:
                    previous_workflows.append(wf)
            if previous_workflows:
                context_str += f"\nPrevious Workflows ({len(previous_workflows)}):"
                for pw in previous_workflows[:3]:
                    context_str += f"\n- Workflow Status: {pw.workflow_status}, Stage: {pw.workflow_stage}, Priority: {pw.priority}"

    # 3. Every customer message performs knowledge retrieval
    retrieval_start = time.monotonic()
    knowledge_service = KnowledgeService()
    search_result = knowledge_service.search(message)
    context_parts = []
    for r in search_result.results[:5]:
        if r["source"] == "faq":
            context_parts.append(f"Q: {r['question']}\nA: {r['answer']}")
        elif r["source"] == "policy":
            context_parts.append(f"Policy: {r['title']}\n{r['summary']}")
        elif r["source"] == "product":
            context_parts.append(f"Product: {r['name']}\n{r['description']}")

    context_str_knowledge = "\n\n".join(context_parts) if context_parts else ""
    context_used = len(context_parts) > 0
    retrieval_latency = (time.monotonic() - retrieval_start) * 1000
    logger.info("rag_retrieval_latency", latency_ms=retrieval_latency)

    # 4. Formulate System Prompt
    ai_gateway = get_ai_gateway()

    # Intent detection & state cache lookup
    state = _CONVERSATION_STATES.get(interaction_id, {
        "intent": "Unknown",
        "flow_stage": "greeting",
        "collected_info": {},
        "missing_info": [],
        "customer_preferences": {},
        "clarification_needed": False,
        "escalate_to_human": False
    })

    history_json = json.dumps(history)
    analysis_prompt = (
        f"{_INTENT_ANALYZER_PROMPT}\n\n"
        f"CURRENT CONVERSATION STATE:\n{json.dumps(state)}\n\n"
        f"USER MESSAGE: '{message}'\n"
        f"HISTORY:\n{history_json}\n\n"
        f"Respond ONLY with the updated state JSON."
    )

    try:
        analysis_response = await ai_gateway.chat(
            messages=[ChatMessage(role="user", content=analysis_prompt)],
        )
        content = analysis_response.message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        updated_state = json.loads(content)
        if "intent" in updated_state:
            state = updated_state
            _CONVERSATION_STATES[interaction_id] = state
            logger.info("conversation_engine_intent_detected", intent=state["intent"], stage=state["flow_stage"])
    except Exception as exc:
        logger.warning("conversation_engine_intent_detection_failed", error=str(exc))

    intent = state.get("intent", "Unknown")
    if intent == "New Policy Purchase":
        intent_prompt = _PROMPT_NEW_POLICY_PURCHASE
    elif intent in ["Product Inquiry", "Coverage Inquiry", "Quote Request"]:
        intent_prompt = _PROMPT_PRODUCT_INQUIRY
    elif intent == "Claims":
        intent_prompt = _PROMPT_CLAIMS
    elif intent == "Complaint":
        intent_prompt = _PROMPT_COMPLAINT
    elif intent == "Policy Renewal":
        intent_prompt = _PROMPT_RENEWAL
    else:
        intent_prompt = "[INTENT: GENERAL/SMALL TALK]\nAnswer the customer query warmly, professionally, and naturally."

    system_prompt = _BASE_SYSTEM_PROMPT + "\n" + intent_prompt

    # Inject memory and state
    state_context = (
        f"\n\n[CONVERSATION CONTEXT & MEMORY]\n"
        f"- Current Active Intent: {intent}\n"
        f"- Current Flow Stage: {state.get('flow_stage', 'greeting')}\n"
        f"- Already Collected Info: {json.dumps(state.get('collected_info', {}))}\n"
        f"- Remaining Info to Collect: {json.dumps(state.get('missing_info', []))}\n"
        f"- Customer Preferences: {json.dumps(state.get('customer_preferences', {}))}\n"
    )
    system_prompt += state_context

    if state.get("clarification_needed", False):
        system_prompt += "\n- IMPORTANT: The user's input was ambiguous or STT confidence was low. You MUST ask a clarification question (e.g. 'Did you mean motorcycle insurance?').\n"

    if state.get("escalate_to_human", False):
        system_prompt += "\n- IMPORTANT: Hand over the call to a human agent professionally (e.g. 'Let me transfer you to a customer care advisor now.').\n"

    if context_str:
        system_prompt += f"\n\nCustomer History Context:\n{context_str}"
    if context_used:
        system_prompt += f"\n\nRetrieved Knowledge Base Context (LuMay Products):\n{context_str_knowledge}"

    chat_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in history]

    return {
        "interaction": interaction,
        "history": history,
        "chat_messages": chat_messages,
        "system_prompt": system_prompt,
        "context_used": context_used,
        "knowledge_service": knowledge_service,
        "ai_gateway": ai_gateway,
    }


async def _finalize_turn(
    ctx: dict,
    message: str,
    ai_content: str,
    provider_used: str,
    interaction_service,
) -> dict:
    """Shared post-processing for a conversation turn: persists the assistant
    response, fires timeline hooks, syncs the SyntheticStore, kicks off
    background complaint intelligence, and builds the standard response dict.
    """
    interaction = ctx["interaction"]
    history = ctx["history"]
    context_used = ctx["context_used"]
    knowledge_service = ctx["knowledge_service"]

    from domains.conversation import integration_hooks as conversation_hooks

    history.append({
        "role": "assistant",
        "content": ai_content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    await interaction_service._repository.update(interaction.id, transcript=json.dumps(history))

    await conversation_hooks.on_message(
        interaction_service._repository._session,
        interaction.id,
        "assistant",
        interaction.channel,
        ai_content,
    )
    await conversation_hooks.publish_ai_typing(
        interaction_service._repository._session, interaction.id, False
    )

    # Synchronize interaction update in SyntheticStore
    store = get_synthetic_store()
    for item in store.get("interactions"):
        if str(item.get("id")) == str(interaction.id):
            item["transcript"] = json.dumps(history)
            break

    # 5. Run Complaint Intelligence asynchronously in the background so it doesn't block LLM response latency
    asyncio.create_task(run_complaint_intelligence_async(interaction.id, message))

    # 6. Format output history
    output_messages = []
    for msg in history:
        try:
            ts = datetime.fromisoformat(msg["timestamp"])
        except (ValueError, KeyError):
            ts = datetime.now(timezone.utc)
        output_messages.append(ChatMessageResponse(role=msg["role"], content=msg["content"], timestamp=ts))

    # Inject search knowledge articles/sources into the final analysis output
    matching_docs = knowledge_service.search(message).results[:3]
    knowledge_articles = []
    for doc in matching_docs:
        title = doc.get("title") or doc.get("name") or doc.get("question") or "Knowledge Article"
        relevance = doc.get("score", 0.85)
        knowledge_articles.append({
            "title": title,
            "relevance": relevance
        })

    from ai.intelligence.models import ComplaintAnalysis, ComplaintDetection
    default_detection = ComplaintDetection(is_complaint=False, confidence=1.0)
    analysis = ComplaintAnalysis(detection=default_detection)
    analysis_dict = asdict(analysis)
    analysis_dict["knowledge_articles"] = knowledge_articles

    return {
        "answer": ai_content,
        "messages": [msg.model_dump() for msg in output_messages],
        "ai_analysis": analysis_dict,
        "context_used": context_used,
        "auto_triaged": False,
        "complaint_id": None,
        "workflow_id": None,
        "provider_used": provider_used,
    }


async def process_conversation(
    interaction_id: uuid.UUID,
    message: str,
    interaction_service,
    complaint_service,
    workflow_service,
    notification_service,
) -> dict:
    import time
    logger.info("process_conversation_started", interaction_id=str(interaction_id), message_length=len(message))

    ctx = await _prepare_turn(interaction_id, message, interaction_service, complaint_service, workflow_service)
    if ctx is None:
        return _not_found_response()

    from domains.conversation import integration_hooks as conversation_hooks

    ai_gateway = ctx["ai_gateway"]
    chat_messages = ctx["chat_messages"]
    system_prompt = ctx["system_prompt"]
    provider_used = "unknown"
    logger.info(
        "conversation_engine_calling_ai_gateway",
        interaction_id=str(interaction_id),
        message_count=len(chat_messages),
    )
    await conversation_hooks.publish_ai_typing(
        interaction_service._repository._session, interaction_id, True
    )
    try:
        llm_start = time.monotonic()
        ai_response = await ai_gateway.chat(
            messages=chat_messages,
            system_prompt=system_prompt,
        )
        ai_content = ai_response.message.content
        provider_used = ai_gateway.active_provider_name
        llm_latency = (time.monotonic() - llm_start) * 1000
        logger.info(
            "conversation_engine_ai_response_received",
            interaction_id=str(interaction_id),
            provider=provider_used,
            latency_ms=llm_latency,
            response_length=len(ai_content),
        )
        logger.info("llm_generation_latency", latency_ms=llm_latency)
    except Exception as exc:
        logger.error("conversation_engine_ai_gateway_failed", error=str(exc))
        ai_content = (
            "I apologise, but I am experiencing a temporary technical issue. "
            "Your message has been recorded and a member of our team will follow up with you shortly. "
            "For urgent matters, please call 800-LUMAY-1."
        )
        provider_used = "fallback"

    return await _finalize_turn(ctx, message, ai_content, provider_used, interaction_service)


async def process_conversation_stream(
    interaction_id: uuid.UUID,
    message: str,
    interaction_service,
    complaint_service,
    workflow_service,
    notification_service,
):
    """Streaming counterpart to process_conversation, for the voice pipeline —
    yields {"type": "chunk", "text": str} as tokens arrive from the AI
    gateway so TTS can start speaking the first sentence immediately, then a
    final {"type": "done", ...} event carrying the same response shape
    process_conversation returns synchronously (once all post-processing —
    transcript persistence, timeline hooks, complaint-intelligence kick-off —
    has run). The blocking process_conversation is untouched and remains the
    text/webchat code path.
    """
    import time
    logger.info("process_conversation_stream_started", interaction_id=str(interaction_id), message_length=len(message))

    ctx = await _prepare_turn(interaction_id, message, interaction_service, complaint_service, workflow_service)
    if ctx is None:
        yield {"type": "done", **_not_found_response()}
        return

    from domains.conversation import integration_hooks as conversation_hooks

    ai_gateway = ctx["ai_gateway"]
    chat_messages = ctx["chat_messages"]
    system_prompt = ctx["system_prompt"]
    provider_used = "unknown"
    logger.info(
        "conversation_engine_calling_ai_gateway_stream",
        interaction_id=str(interaction_id),
        message_count=len(chat_messages),
    )
    await conversation_hooks.publish_ai_typing(
        interaction_service._repository._session, interaction_id, True
    )

    chunks: list[str] = []
    try:
        llm_start = time.monotonic()
        first_chunk_latency: float | None = None
        async for chunk in ai_gateway.stream(messages=chat_messages, system_prompt=system_prompt):
            if not chunk:
                continue
            if first_chunk_latency is None:
                first_chunk_latency = (time.monotonic() - llm_start) * 1000
                logger.info("conversation_engine_stream_ttft_ms", latency_ms=first_chunk_latency)
            chunks.append(chunk)
            yield {"type": "chunk", "text": chunk}
        ai_content = "".join(chunks)
        if not ai_content:
            raise RuntimeError("empty streaming response")
        provider_used = ai_gateway.active_provider_name
        llm_latency = (time.monotonic() - llm_start) * 1000
        logger.info(
            "conversation_engine_ai_response_received",
            interaction_id=str(interaction_id),
            provider=provider_used,
            latency_ms=llm_latency,
            response_length=len(ai_content),
        )
        logger.info("llm_generation_latency", latency_ms=llm_latency)
    except Exception as exc:
        logger.error("conversation_engine_ai_gateway_stream_failed", error=str(exc))
        ai_content = (
            "I apologise, but I am experiencing a temporary technical issue. "
            "Your message has been recorded and a member of our team will follow up with you shortly. "
            "For urgent matters, please call 800-LUMAY-1."
        )
        provider_used = "fallback"
        yield {"type": "chunk", "text": ai_content}

    result = await _finalize_turn(ctx, message, ai_content, provider_used, interaction_service)
    yield {"type": "done", **result}

async def run_complaint_intelligence_async(
    interaction_id: uuid.UUID,
    message: str,
) -> None:
    """Asynchronously runs Complaint Intelligence, Workflow assignment, and Notifications in the background."""
    import time
    import asyncio
    from app.platform.database.session import get_session_factory
    
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            # 1. Instantiate repositories & services with independent db session
            from domains.interaction.repositories.interaction_repository import InteractionRepository
            from domains.interaction.services.interaction_service import InteractionService
            from domains.complaint.repositories.complaint_repository import ComplaintRepository
            from domains.complaint.services.complaint_service import ComplaintService
            from domains.workflow.repositories.workflow_repository import WorkflowRepository
            from domains.workflow.services.workflow_service import WorkflowService
            from domains.notification.repositories.notification_repository import NotificationRepository
            from domains.notification.services.notification_service import NotificationService
            from domains.customer.repositories.customer_repository import CustomerRepository
            from domains.complaint.schemas.complaint_schemas import ComplaintCreate
            from domains.workflow.schemas.workflow_schemas import WorkflowCreate
            from domains.notification.schemas.notification_schemas import NotificationCreate
            from domains.notification.constants.notification_constants import NotificationType, NotificationChannel
            from domains.interaction.constants.interaction_constants import InteractionChannel
            from domains.conversation import integration_hooks as conversation_hooks

            interaction_repo = InteractionRepository(session=db)
            interaction_service = InteractionService(repository=interaction_repo)
            
            complaint_repo = ComplaintRepository(session=db)
            customer_repo = CustomerRepository(session=db)
            complaint_service = ComplaintService(
                repository=complaint_repo,
                customer_repository=customer_repo,
                interaction_repository=interaction_repo,
            )
            
            workflow_repo = WorkflowRepository(session=db)
            workflow_service = WorkflowService(repository=workflow_repo, complaint_repository=complaint_repo)
            
            notification_repo = NotificationRepository(session=db)
            notification_service = NotificationService(repository=notification_repo, workflow_repository=workflow_repo)
            
            # Fetch interaction
            interaction = await interaction_service.get_interaction(interaction_id)
            if not interaction:
                return
                
            # Fetch customer
            customer = None
            if interaction.customer_ref:
                try:
                    cust_uuid = uuid.UUID(interaction.customer_ref)
                    customer = await customer_repo.get_by_id(cust_uuid)
                except ValueError:
                    customer = await customer_repo.get_by_external_ref(interaction.customer_ref)
                    if not customer:
                        customer = await customer_repo.get_by_email(interaction.customer_ref)
                
            logger.info("bg_complaint_intel_started", interaction_id=str(interaction_id))
            intel_start = time.monotonic()
            intel_service = ComplaintIntelligenceService()
            detection = await intel_service.detect_complaint(message)
            is_complaint = detection.is_complaint
            confidence = detection.confidence

            if is_complaint and confidence >= 0.90:
                from ai.intelligence.pipeline import build_metadata
                from ai.intelligence.models import ComplaintAnalysis
                
                (
                    sentiment,
                    themes,
                    severity,
                    escalation,
                    priority,
                    summary,
                    root_cause,
                    resolution,
                    language,
                ) = await asyncio.gather(
                    intel_service.analyze_sentiment(message),
                    intel_service.extract_themes(message),
                    intel_service.assess_severity(message),
                    intel_service.assess_escalation_risk(message),
                    intel_service.recommend_priority(message),
                    intel_service.summarize(message),
                    intel_service.analyze_root_cause(message),
                    intel_service.recommend_resolution(message),
                    intel_service.detect_language(message),
                )
                total_metadata = build_metadata(
                    model_used=detection.metadata.model_used if detection.metadata else "",
                    processing_time_ms=0.0,
                    token_usage={},
                    prompt_name="complaint/analysis/complete",
                    explanation="Optimized complaint analysis pipeline",
                )
                analysis = ComplaintAnalysis(
                    detection=detection,
                    sentiment=sentiment,
                    themes=themes,
                    severity=severity,
                    escalation=escalation,
                    priority=priority,
                    summary=summary,
                    root_cause=root_cause,
                    resolution=resolution,
                    language=language,
                    metadata=total_metadata,
                )
                
                category_map = {
                    "claims": "claims",
                    "billing": "billing",
                    "policy": "service",
                    "service": "service",
                    "technical": "compliance",
                }
                
                # Check existing complaint
                from sqlalchemy import select
                from domains.complaint.models.complaint import Complaint
                stmt = select(Complaint).where(Complaint.interaction_id == interaction.id)
                result = await db.execute(stmt)
                existing_complaint = result.scalars().first()
                
                if not existing_complaint:
                    cust_id = customer.id if customer else None
                    cat_val = (analysis.themes.primary_theme or "").lower()
                    if "billing" in cat_val or "financial" in cat_val:
                        category = "billing"
                    elif "claims" in cat_val:
                        category = "claims"
                    elif "policy" in cat_val:
                        category = "policy"
                    elif "digital" in cat_val or "technical" in cat_val:
                        category = "technical"
                    else:
                        category = "service"
                        
                    source_map = {
                        InteractionChannel.WEB_FORM: "web_chat",
                        InteractionChannel.EMAIL: "email",
                        InteractionChannel.WHATSAPP: "whatsapp",
                        InteractionChannel.VOICE: "phone",
                    }
                    source_val = source_map.get(interaction.channel, "web_chat")
                    
                    complaint_create = ComplaintCreate(
                        customer_id=cust_id,
                        interaction_id=interaction.id,
                        title=f"Auto-Triaged: {analysis.summary.summary[:50]}...",
                        description=message,
                        category=category,
                        priority=analysis.priority.priority.lower() or "medium",
                        severity=analysis.severity.severity.lower() or "moderate",
                        status="submitted",
                        source=source_val,
                        channel=source_val,
                    )
                    complaint, _ = await complaint_service.create_complaint(complaint_create)
                    await db.refresh(complaint)
                    complaint_id = complaint.id
                    await conversation_hooks.on_complaint_created(db, interaction.id, complaint)

                    assigned_team = category_map.get(category, "compliance")
                    workflow_create = WorkflowCreate(
                        complaint_id=complaint.id,
                        current_queue=assigned_team,
                        assigned_team=assigned_team,
                        assigned_agent_id=None,
                    )
                    workflow, _ = await workflow_service.create_workflow(workflow_create)
                    workflow_id = workflow.id
                    await conversation_hooks.on_workflow_created(db, interaction.id, workflow)

                    notification_create = NotificationCreate(
                        workflow_id=workflow.id,
                        complaint_id=complaint.id,
                        notification_type=NotificationType.ALERT,
                        channel=NotificationChannel.SMS if interaction.channel == InteractionChannel.WHATSAPP else NotificationChannel.EMAIL,
                        recipient=interaction.customer_ref or "customer@email.com",
                        subject="Complaint Registered",
                        message_body=f"Dear Customer, your complaint has been registered as {complaint.complaint_number} and is being reviewed by our {assigned_team} team.",
                    )
                    notification = await notification_service.create_notification(notification_create)
                    await conversation_hooks.on_notification_created(db, interaction.id, notification[0])

                    # Sync with SyntheticStore
                    store = get_synthetic_store()
                    complaint_dict = {
                        "id": str(complaint_id),
                        "complaint_number": complaint.complaint_number or f"COMP-{len(store.get('complaints')) + 1:05d}",
                        "customer_id": str(cust_id) if cust_id else None,
                        "interaction_id": str(interaction.id),
                        "title": complaint.title,
                        "description": complaint.description,
                        "category": complaint.category,
                        "priority": complaint.priority.lower() if hasattr(complaint.priority, 'lower') else str(complaint.priority),
                        "severity": complaint.severity.lower() if hasattr(complaint.severity, 'lower') else str(complaint.severity),
                        "status": "under_review",
                        "source": "chat" if interaction.channel == InteractionChannel.WEB_FORM else str(interaction.channel.value),
                        "assigned_queue": assigned_team,
                        "metadata": {
                            "ai_sentiment": analysis.sentiment.sentiment,
                            "ai_sentiment_polarity": analysis.sentiment.polarity,
                            "ai_theme": analysis.themes.primary_theme,
                        },
                        "created_at": complaint.created_at.isoformat() if complaint.created_at else datetime.now(timezone.utc).isoformat(),
                    }
                    store.get("complaints").append(complaint_dict)
                    
                    workflow_dict = {
                        "id": str(workflow_id),
                        "complaint_id": str(complaint_id),
                        "assigned_team": workflow.assigned_team,
                        "current_queue": workflow.current_queue,
                        "assigned_agent_id": None,
                        "workflow_status": "active",
                        "workflow_stage": "queued",
                        "sla_status": "within_sla",
                        "due_at": workflow.due_at.isoformat() if workflow.due_at else None,
                        "created_at": workflow.created_at.isoformat() if hasattr(workflow.created_at, 'isoformat') else str(workflow.created_at),
                    }
                    store.get("workflows").append(workflow_dict)
                    
                    notification_dict = {
                        "id": str(uuid.uuid4()),
                        "workflow_id": str(workflow_id),
                        "complaint_id": str(complaint_id),
                        "notification_type": "alert",
                        "channel": "sms" if interaction.channel == InteractionChannel.WHATSAPP else "email",
                        "recipient": interaction.customer_ref or "customer@email.com",
                        "subject": "Complaint Registered",
                        "message_body": f"Dear Customer, your complaint has been registered as {complaint.complaint_number} and is being reviewed by our {assigned_team} team.",
                        "status": "sent",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    store.get("notifications").append(notification_dict)
                    
                    # Update active voice session metadata if transcript manager exists
                    try:
                        from voice.transcript_manager import get_transcript_manager
                        tm = get_transcript_manager()
                        for sid, s in tm._sessions.items():
                            if str(s.get("interaction_id")) == str(interaction_id):
                                await tm.update_metadata(sid, "complaint_id", str(complaint_id))
                                await tm.update_metadata(sid, "workflow_id", str(workflow_id))
                                break
                    except Exception:
                        pass
                        
                    # Log success
                    logger.info("bg_complaint_intel_completed", complaint_id=str(complaint_id), workflow_id=str(workflow_id))
            
            intel_latency = (time.monotonic() - intel_start) * 1000
            logger.info("bg_complaint_intelligence_latency", latency_ms=intel_latency, is_complaint=is_complaint)

            # This task owns its own session (independent of the request's, which
            # is long gone by the time this runs) — repository .add() only
            # flushes, so without an explicit commit here everything created
            # above (complaint/workflow/notification) is silently rolled back
            # when the `async with session_factory()` block below closes it.
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("bg_complaint_intel_failed", error=str(exc))
