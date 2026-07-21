"""Integration hooks — the only new code that touches existing channel flows.

Every function here is self-contained (builds its own repositories/services
from the `AsyncSession` it's given) and fails open: any exception is caught
and logged as a warning, never propagated, so a bug in the new conversation
layer can never break webchat, voice, or complaint filing. This mirrors how
`SessionManager` already tolerates `interaction_service` failures today.

Functions that reuse a request-scoped session (`on_interaction_started`,
`on_message`, the three `run_complaint_intelligence_async` hooks, and all the
Phase 2 lifecycle hooks below) do NOT commit — whatever owns that session
(the `get_db()` FastAPI dependency, or `run_complaint_intelligence_async`'s
own session) owns the commit, and these hooks must not change that
transaction's boundaries. `on_complaint_filed_manually` is the one exception:
it runs via FastAPI `BackgroundTasks` with no ambient session, so it opens
and commits its own.

Channel-adapter contract (Sprint 28 Phase 2 — "prepare abstraction for
WhatsApp/Email"): `ChannelResolver` already maps `"whatsapp"`/`"email"` raw
strings to `ConversationChannel` values. Any future inbound handler for a new
channel (a real WhatsApp Business webhook, an inbound-email processor, later
SMS/Teams/mobile) only needs to make two calls to plug into the unified
conversation timeline, in order:
  1. `on_interaction_started(session, customer_ref, "<channel>", interaction_id)`
     once per session/thread, right after creating the underlying `Interaction`.
  2. `on_message(session, interaction_id, role, "<channel>", content)` once per
     turn (`role` one of "user"/"customer", "assistant"/"ai", "agent"/"employee").
No other wiring is required — status transitions, participant tracking, and
"last activity" are all handled inside `on_message` itself.
"""

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.logging import get_logger
from domains.conversation.constants.conversation_constants import (
    ConversationMessageType,
    ConversationParticipantType,
    ConversationPriority,
    ConversationStatus,
)
from domains.conversation.event_bus import publish_conversation_event
from domains.conversation.repositories.channel_repository import ConversationChannelRepository
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.repositories.message_repository import ConversationMessageRepository
from domains.conversation.repositories.participant_repository import (
    ConversationParticipantRepository,
)
from domains.conversation.services.channel_resolver import ChannelResolver
from domains.conversation.services.conversation_factory import ConversationFactory
from domains.conversation.services.conversation_service import ConversationService
from domains.conversation.services.event_service import ConversationEventService
from domains.conversation.services.message_service import MessageService
from domains.conversation.services.participant_service import ConversationParticipantService
from domains.conversation.presence import get_presence_registry

logger = get_logger(__name__)

_SENDER_TYPE_BY_ROLE: dict[str, ConversationParticipantType] = {
    "user": ConversationParticipantType.CUSTOMER,
    "customer": ConversationParticipantType.CUSTOMER,
    "assistant": ConversationParticipantType.AI,
    "ai": ConversationParticipantType.AI,
    "agent": ConversationParticipantType.EMPLOYEE,
    "employee": ConversationParticipantType.EMPLOYEE,
    "system": ConversationParticipantType.SYSTEM,
}

# Status auto-transition matrix (Sprint 28 Phase 2). Applied best-effort via
# `_try_transition` — an unreachable target for the current state is skipped,
# never raised, so a message/lifecycle event can never break its caller.
_MESSAGE_STATUS_BY_SENDER: dict[ConversationParticipantType, ConversationStatus] = {
    ConversationParticipantType.AI: ConversationStatus.AI_HANDLING,
    ConversationParticipantType.EMPLOYEE: ConversationStatus.HUMAN_HANDLING,
}
_COMPLAINT_STATUS_TARGETS: dict[str, ConversationStatus] = {
    "complaint.escalated": ConversationStatus.ESCALATED,
    "complaint.resolved": ConversationStatus.RESOLVED,
    "complaint.closed": ConversationStatus.CLOSED,
}
_WORKFLOW_STATUS_TARGETS: dict[str, ConversationStatus] = {
    "workflow.escalated": ConversationStatus.ESCALATED,
    "workflow.completed": ConversationStatus.RESOLVED,
    "workflow.archived": ConversationStatus.CLOSED,
}


async def _try_transition(
    conversation_service: ConversationService,
    conversation_id: uuid.UUID,
    target: ConversationStatus,
) -> None:
    """Best-effort status transition — skips silently if `target` isn't
    reachable from the conversation's current state (Phase 1's
    `_ALLOWED_TRANSITIONS`), or if the conversation is already there."""
    try:
        await conversation_service.update_status(conversation_id, target)
    except Exception as exc:
        logger.debug(
            "conversation_hook_status_transition_skipped",
            conversation_id=str(conversation_id),
            target=target,
            error=str(exc),
        )


def _build_factory(session: AsyncSession) -> ConversationFactory:
    conversation_repo = ConversationRepository(session=session)
    return ConversationFactory(
        conversation_repository=conversation_repo,
        conversation_service=ConversationService(repository=conversation_repo),
        channel_repository=ConversationChannelRepository(session=session),
        participant_repository=ConversationParticipantRepository(session=session),
    )


async def _resolve_customer_id(
    session: AsyncSession, customer_ref: str | None
) -> uuid.UUID | None:
    """Same UUID -> external_ref -> email resolution order already used inline
    in `conversation_engine.py`, duplicated here to avoid touching that file."""
    if not customer_ref:
        return None
    try:
        return uuid.UUID(customer_ref)
    except ValueError:
        pass
    try:
        from domains.customer.repositories.customer_repository import CustomerRepository

        customer_repo = CustomerRepository(session=session)
        customer = await customer_repo.get_by_external_ref(customer_ref)
        if not customer:
            customer = await customer_repo.get_by_email(customer_ref)
        return customer.id if customer else None
    except Exception as exc:
        logger.debug("conversation_hook_customer_resolve_failed", error=str(exc))
        return None


async def on_interaction_started(
    session: AsyncSession,
    customer_ref: str | None,
    channel_raw: str,
    interaction_id: uuid.UUID,
    complaint_id: uuid.UUID | None = None,
) -> uuid.UUID | None:
    """Call right after a channel entry point creates an `Interaction` (webchat/
    whatsapp/email session start, or a voice session). Links the touchpoint to
    a new-or-reused `Conversation` via the cross-channel merge rule."""
    try:
        channel = ChannelResolver.resolve(channel_raw)
        customer_id = await _resolve_customer_id(session, customer_ref)
        factory = _build_factory(session)
        conversation, created = await factory.get_or_create(
            customer_id=customer_id,
            channel=channel,
            complaint_id=complaint_id,
            external_ref_type="interaction_id",
            external_ref_id=str(interaction_id),
        )
        if created:
            publish_conversation_event(
                str(conversation.id), "conversation.created", {"channel": channel}
            )
        return conversation.id
    except Exception as exc:
        logger.warning(
            "conversation_hook_on_interaction_started_failed",
            error=str(exc),
            interaction_id=str(interaction_id),
        )
        return None


async def on_message(
    session: AsyncSession,
    interaction_id: uuid.UUID,
    role: str,
    channel_raw: str,
    content: str,
    *,
    message_type: ConversationMessageType = ConversationMessageType.TEXT,
) -> None:
    """Call every time a chat turn (or a voice transcript segment) is persisted
    to an `Interaction`. Mirrors it onto the linked `Conversation` as a proper
    `ConversationMessage` row, then auto-advances status and last-activity
    (CUSTOMER/AI participants are already seeded once at conversation creation
    by `ConversationFactory`, so this does not re-register them)."""
    try:
        channel_repo = ConversationChannelRepository(session=session)
        link = await channel_repo.get_by_external_ref("interaction_id", str(interaction_id))
        if link is None:
            return
        channel = ChannelResolver.resolve(channel_raw)
        sender_type = _SENDER_TYPE_BY_ROLE.get(
            (role or "").lower(), ConversationParticipantType.SYSTEM
        )
        message_service = MessageService(repository=ConversationMessageRepository(session=session))
        message = await message_service.add_message(
            link.conversation_id, sender_type, channel, content, message_type=message_type
        )
        publish_conversation_event(
            str(link.conversation_id),
            "message",
            {
                "id": str(message.id),
                "sender_type": sender_type,
                "channel": channel,
                "message_type": message_type,
                "content": content,
            },
        )

        conversation_repo = ConversationRepository(session=session)
        conversation_service = ConversationService(repository=conversation_repo)
        if sender_type == ConversationParticipantType.CUSTOMER:
            conversation = await conversation_service.get_conversation(link.conversation_id)
            target = (
                ConversationStatus.WAITING_FOR_AGENT
                if conversation.human_handling
                else ConversationStatus.ACTIVE
            )
            await _try_transition(conversation_service, link.conversation_id, target)
        else:
            target = _MESSAGE_STATUS_BY_SENDER.get(sender_type)
            if target is not None:
                await _try_transition(conversation_service, link.conversation_id, target)

        await conversation_repo.touch(link.conversation_id)

        # Agent Assist (Sprint 28 Phase 5) — fire-and-forget, own session (like
        # run_complaint_intelligence_async), throttled internally so this does
        # NOT regenerate on every message. Fires regardless of sender_type or
        # ai_handling/human_handling, so it keeps assisting silently after an
        # employee takes over (Phase 4 scenario 3).
        asyncio.create_task(_maybe_regenerate_agent_assist(link.conversation_id))
    except Exception as exc:
        logger.warning(
            "conversation_hook_on_message_failed",
            error=str(exc),
            interaction_id=str(interaction_id),
        )


async def _maybe_regenerate_agent_assist(conversation_id: uuid.UUID) -> None:
    try:
        from app.platform.database.session import get_session_factory
        from domains.agent_assist.services.agent_assist_service import (
            regenerate_agent_assist_insight,
        )

        session_factory = get_session_factory()
        async with session_factory() as bg_session:
            await regenerate_agent_assist_insight(bg_session, conversation_id, force=False)
            await bg_session.commit()
    except Exception as exc:
        logger.warning(
            "agent_assist_regeneration_failed",
            error=str(exc),
            conversation_id=str(conversation_id),
        )


async def publish_ai_typing(session: AsyncSession, interaction_id: uuid.UUID, is_typing: bool) -> None:
    """Called around the AI gateway call in `conversation_engine.process_conversation`
    (right before it starts, and once the reply is persisted) — the "AI generating
    response" live indicator. Ephemeral only, via `PresenceRegistry`/SSE, never a
    `ConversationEvent` row (same as `on_message`'s customer/employee typing)."""
    try:
        channel_repo = ConversationChannelRepository(session=session)
        link = await channel_repo.get_by_external_ref("interaction_id", str(interaction_id))
        if link is None:
            return
        conversation_id = str(link.conversation_id)
        await get_presence_registry().set_typing(
            conversation_id, ConversationParticipantType.AI, is_typing
        )
        publish_conversation_event(
            conversation_id,
            "typing",
            {"participant_type": ConversationParticipantType.AI, "is_typing": is_typing},
        )
    except Exception as exc:
        logger.warning(
            "conversation_hook_publish_ai_typing_failed",
            error=str(exc),
            interaction_id=str(interaction_id),
        )


async def _record_event_for_interaction(
    session: AsyncSession,
    interaction_id: uuid.UUID,
    event_type: str,
    source_domain: str,
    payload: dict[str, Any] | None,
    *,
    complaint_id: uuid.UUID | None = None,
    escalate: bool = False,
) -> None:
    channel_repo = ConversationChannelRepository(session=session)
    link = await channel_repo.get_by_external_ref("interaction_id", str(interaction_id))
    if link is None:
        return

    event_service = ConversationEventService(repository=ConversationEventRepository(session=session))
    event = await event_service.record_event(link.conversation_id, event_type, source_domain, payload)
    publish_conversation_event(
        str(link.conversation_id),
        "event",
        {"id": str(event.id), "event_type": event_type, "source_domain": source_domain, "payload": payload},
    )

    conversation_repo = ConversationRepository(session=session)
    conversation_service = ConversationService(repository=conversation_repo)
    if complaint_id is not None:
        await conversation_service.link_complaint(link.conversation_id, complaint_id)
    if escalate:
        await _try_transition(conversation_service, link.conversation_id, ConversationStatus.ESCALATED)

    await conversation_repo.touch(link.conversation_id)


async def _record_event_for_complaint(
    session: AsyncSession,
    complaint_id: uuid.UUID,
    event_type: str,
    source_domain: str,
    payload: dict[str, Any] | None,
    *,
    status_target: ConversationStatus | None = None,
) -> uuid.UUID | None:
    """The Phase 2 counterpart to `_record_event_for_interaction`, keyed by
    `complaint_id` instead of `interaction_id` — this is what lets a complaint
    lifecycle action (assign/escalate/resolve/...) find its conversation even
    when it didn't originate from a chat/voice touchpoint (e.g. a complaint
    filed manually and only linked via `on_complaint_filed_manually`)."""
    conversation_repo = ConversationRepository(session=session)
    conversation_service = ConversationService(repository=conversation_repo)
    conversation = await conversation_service.get_by_complaint_id(complaint_id)
    if conversation is None:
        return None

    event_service = ConversationEventService(repository=ConversationEventRepository(session=session))
    event = await event_service.record_event(conversation.id, event_type, source_domain, payload)
    publish_conversation_event(
        str(conversation.id),
        "event",
        {"id": str(event.id), "event_type": event_type, "source_domain": source_domain, "payload": payload},
    )

    if status_target is not None:
        await _try_transition(conversation_service, conversation.id, status_target)

    await conversation_repo.touch(conversation.id)
    return conversation.id


async def on_complaint_created(
    session: AsyncSession, interaction_id: uuid.UUID, complaint: Any
) -> None:
    try:
        await _record_event_for_interaction(
            session,
            interaction_id,
            "complaint.created",
            "complaint",
            {"complaint_id": str(complaint.id), "complaint_number": complaint.complaint_number},
            complaint_id=complaint.id,
            escalate=True,
        )
    except Exception as exc:
        logger.warning("conversation_hook_on_complaint_created_failed", error=str(exc))


async def on_workflow_created(
    session: AsyncSession, interaction_id: uuid.UUID, workflow: Any
) -> None:
    try:
        await _record_event_for_interaction(
            session,
            interaction_id,
            "workflow.started",
            "workflow",
            {"workflow_id": str(workflow.id), "assigned_team": workflow.assigned_team},
        )
    except Exception as exc:
        logger.warning("conversation_hook_on_workflow_created_failed", error=str(exc))


async def on_notification_created(
    session: AsyncSession, interaction_id: uuid.UUID, notification: Any
) -> None:
    try:
        await _record_event_for_interaction(
            session,
            interaction_id,
            "notification.created",
            "notification",
            {"notification_id": str(notification.id)},
        )
    except Exception as exc:
        logger.warning("conversation_hook_on_notification_created_failed", error=str(exc))


async def on_complaint_filed_manually(
    customer_id: uuid.UUID | None, complaint_id: uuid.UUID, complaint_number: str | None
) -> None:
    """Background task for the manual `POST /complaints` / `POST /complaints/ingest`
    paths, which have no prior `Interaction`. Creates/links a COMPLAINT-channel
    conversation (or reuses an existing active one for the customer, per the
    cross-channel merge rule) so a complaint filed via the modal is no longer
    disconnected from the conversation record. Opens and commits its own
    session since `BackgroundTasks` run after the response with no ambient session.
    """
    if customer_id is None:
        return
    try:
        from app.platform.database.session import get_session_factory

        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                factory = _build_factory(session)
                conversation, created = await factory.get_or_create(
                    customer_id=customer_id,
                    channel=ChannelResolver.resolve("complaint"),
                    complaint_id=complaint_id,
                    external_ref_type="complaint_id",
                    external_ref_id=str(complaint_id),
                )
                event_service = ConversationEventService(
                    repository=ConversationEventRepository(session=session)
                )
                await event_service.record_event(
                    conversation.id,
                    "complaint.created",
                    "complaint",
                    {"complaint_id": str(complaint_id), "complaint_number": complaint_number},
                )
                await session.commit()
                if created:
                    publish_conversation_event(
                        str(conversation.id), "conversation.created", {"channel": "complaint"}
                    )
                publish_conversation_event(
                    str(conversation.id),
                    "event",
                    {
                        "event_type": "complaint.created",
                        "source_domain": "complaint",
                        "payload": {
                            "complaint_id": str(complaint_id),
                            "complaint_number": complaint_number,
                        },
                    },
                )
            except Exception:
                await session.rollback()
                raise
    except Exception as exc:
        logger.warning(
            "conversation_hook_on_complaint_filed_manually_failed",
            error=str(exc),
            complaint_id=str(complaint_id),
        )


async def _ensure_agent_participant(
    session: AsyncSession, conversation_id: uuid.UUID, agent_id: uuid.UUID | None
) -> None:
    if agent_id is None:
        return
    participant_service = ConversationParticipantService(
        repository=ConversationParticipantRepository(session=session)
    )
    await participant_service.ensure_participant(
        conversation_id, ConversationParticipantType.EMPLOYEE, str(agent_id)
    )


async def on_complaint_lifecycle(
    session: AsyncSession,
    complaint: Any,
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    assigned_agent_id: uuid.UUID | None = None,
) -> None:
    """Records any complaint lifecycle action — update/assign/escalate/resolve/
    close/archive/ai-override/acknowledge/AI-intelligence-result — as a
    `ConversationEvent`. Looked up via `complaint.id`, so this works whether
    the complaint originated from a chat/voice touchpoint or was filed
    manually. `event_type` should be the same routing-key string already
    defined on the corresponding `ComplaintXEvent` (e.g. `"complaint.assigned"`)
    for consistency with the rest of the codebase's event naming."""
    try:
        full_payload: dict[str, Any] = {
            "complaint_id": str(complaint.id),
            "complaint_number": complaint.complaint_number,
        }
        if payload:
            full_payload.update(payload)
        conversation_id = await _record_event_for_complaint(
            session,
            complaint.id,
            event_type,
            "complaint",
            full_payload,
            status_target=_COMPLAINT_STATUS_TARGETS.get(event_type),
        )
        if conversation_id is not None:
            await _ensure_agent_participant(session, conversation_id, assigned_agent_id)
            # Keep the conversation card's priority in sync with its linked
            # complaint — both enums share the same lowercase value scale.
            if getattr(complaint, "priority", None) is not None:
                try:
                    conversation_priority = ConversationPriority(str(complaint.priority))
                    await ConversationRepository(session=session).update(
                        conversation_id, priority=conversation_priority
                    )
                except ValueError:
                    pass
    except Exception as exc:
        logger.warning(
            "conversation_hook_on_complaint_lifecycle_failed", error=str(exc), event_type=event_type
        )


async def on_workflow_lifecycle(
    session: AsyncSession,
    workflow: Any,
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    assigned_agent_id: uuid.UUID | None = None,
) -> None:
    """Same shape as `on_complaint_lifecycle`, keyed by `workflow.complaint_id`
    (every `Workflow` row has a required, non-null `complaint_id`)."""
    try:
        full_payload: dict[str, Any] = {"workflow_id": str(workflow.id)}
        if payload:
            full_payload.update(payload)
        conversation_id = await _record_event_for_complaint(
            session,
            workflow.complaint_id,
            event_type,
            "workflow",
            full_payload,
            status_target=_WORKFLOW_STATUS_TARGETS.get(event_type),
        )
        if conversation_id is not None:
            await _ensure_agent_participant(session, conversation_id, assigned_agent_id)
    except Exception as exc:
        logger.warning(
            "conversation_hook_on_workflow_lifecycle_failed", error=str(exc), event_type=event_type
        )


async def on_notification_recorded(session: AsyncSession, notification: Any) -> None:
    """Call from the direct `POST /notifications` endpoint (manual creation) —
    the AI-triage path already has its own hook, `on_notification_created`,
    keyed by `interaction_id`. This one resolves the conversation via
    `notification.complaint_id`, falling back to `notification.workflow_id`'s
    own `complaint_id` if only the workflow reference is set."""
    try:
        complaint_id = notification.complaint_id
        if complaint_id is None and notification.workflow_id is not None:
            from domains.workflow.repositories.workflow_repository import WorkflowRepository

            workflow = await WorkflowRepository(session=session).get_by_id(notification.workflow_id)
            complaint_id = workflow.complaint_id if workflow else None
        if complaint_id is None:
            return
        await _record_event_for_complaint(
            session,
            complaint_id,
            "notification.created",
            "notification",
            {
                "notification_id": str(notification.id),
                "notification_type": str(notification.notification_type),
                "channel": str(notification.notification_channel),
            },
        )
    except Exception as exc:
        logger.warning("conversation_hook_on_notification_recorded_failed", error=str(exc))


async def on_voice_session_started(
    session: AsyncSession, conversation_id: uuid.UUID | None, room_name: str
) -> None:
    """Call from `SessionManager.create_session`, right after
    `on_interaction_started` — reuses the `conversation_id` it already resolved."""
    if conversation_id is None:
        return
    try:
        event_service = ConversationEventService(repository=ConversationEventRepository(session=session))
        await event_service.record_event(
            conversation_id, "voice.session_started", "voice", {"room_name": room_name}
        )
        publish_conversation_event(
            str(conversation_id),
            "event",
            {"event_type": "voice.session_started", "source_domain": "voice", "payload": {"room_name": room_name}},
        )
        await ConversationRepository(session=session).touch(conversation_id)
    except Exception as exc:
        logger.warning("conversation_hook_on_voice_session_started_failed", error=str(exc))


async def on_voice_session_ended(
    session: AsyncSession,
    interaction_id: uuid.UUID | str,
    started_at: str | None,
    ended_at: str | None,
    room_name: str | None = None,
) -> None:
    """Call from `SessionManager.end_session`. Resolves the conversation via
    `interaction_id` (same channel-link lookup as `on_message`) rather than
    requiring the caller to have kept `conversation_id` around — `end_session`
    only has `session["interaction_id"]` in scope. `started_at`/`ended_at` are
    the ISO-8601 strings already tracked on `TranscriptManager`'s session dict
    (confirmed present, just not previously surfaced) — duration is computed
    here since no pre-computed duration field exists anywhere upstream.
    There is no recording-URL concept anywhere in this codebase today, so the
    payload doesn't invent one."""
    try:
        channel_repo = ConversationChannelRepository(session=session)
        link = await channel_repo.get_by_external_ref("interaction_id", str(interaction_id))
        if link is None:
            return
        conversation_id = link.conversation_id

        duration_seconds: float | None = None
        if started_at and ended_at:
            try:
                start_dt = datetime.fromisoformat(started_at)
                end_dt = datetime.fromisoformat(ended_at)
                duration_seconds = max((end_dt - start_dt).total_seconds(), 0)
            except ValueError:
                duration_seconds = None
        event_service = ConversationEventService(repository=ConversationEventRepository(session=session))
        voice_payload = {
            "room_name": room_name,
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_seconds": duration_seconds,
        }
        await event_service.record_event(conversation_id, "voice.session_ended", "voice", voice_payload)
        publish_conversation_event(
            str(conversation_id),
            "event",
            {"event_type": "voice.session_ended", "source_domain": "voice", "payload": voice_payload},
        )
        await ConversationRepository(session=session).touch(conversation_id)
    except Exception as exc:
        logger.warning("conversation_hook_on_voice_session_ended_failed", error=str(exc))
