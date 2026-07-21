"""Reporting domain service — Customer 360 + Enterprise Analytics (Sprint 29).

Pure read-side composition over existing domain repositories. No new
tables; every number here is a real query (or a Python-side reduction over
real rows, kept portable across the Postgres/SQLite dialects this codebase
runs against) — never synthetic/demo data.
"""

from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from datetime import datetime

from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import ComplaintSummary
from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationStatus,
)
from domains.conversation.presence import get_presence_registry
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.repositories.message_repository import ConversationMessageRepository
from domains.conversation.schemas.conversation_schemas import (
    ConversationResponse,
    ConversationSummary,
    TimelineItem,
)
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.exceptions.customer_exceptions import CustomerNotFoundError
from domains.identity.repositories.user_repository import UserRepository
from domains.reporting.constants.reporting_constants import (
    MESSAGE_RESPONSE_TIME_CONVERSATION_CAP,
    RECENT_CONVERSATIONS_LIMIT,
)
from domains.reporting.schemas.reporting_schemas import (
    AgentAssistSnapshot,
    AiUtilizationTrendPoint,
    AssignedEmployee,
    ConversationAnalyticsSummary,
    ConversationDistributions,
    ConversationStatistics,
    ConversationTrends,
    Customer360Response,
    CustomerActivityTimelineResponse,
    CustomerInfo,
    CustomerOverview,
    EmployeeAnalyticsItem,
    IntentTrendPoint,
    SentimentTrendPoint,
    SupervisorDashboard,
    TrendPoint,
    VoiceVsChat,
)
from app.platform.logging import get_logger
from shared.base_service import BaseService

logger = get_logger(__name__)

_AI_HANDED_OVER = "ai_handed_over"
_CONVERSATION_TRANSFERRED = "conversation_transferred"


class ReportingService(BaseService):
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        event_repository: ConversationEventRepository,
        message_repository: ConversationMessageRepository,
        agent_assist_repository: AgentAssistRepository,
        complaint_repository: ComplaintRepository,
        customer_repository: CustomerRepository,
        user_repository: UserRepository,
    ) -> None:
        self._conversations = conversation_repository
        self._events = event_repository
        self._messages = message_repository
        self._agent_assist = agent_assist_repository
        self._complaints = complaint_repository
        self._customers = customer_repository
        self._users = user_repository
        self._logger = logger

    async def _resolve_employee_names(self, ids: set[uuid.UUID]) -> dict[uuid.UUID, str | None]:
        ids = {i for i in ids if i is not None}
        if not ids:
            return {}
        users = await self._users.list_by_ids(list(ids))
        names = {u.id: u.full_name for u in users}
        return {i: names.get(i) for i in ids}

    # ── Customer 360 ─────────────────────────────────────────────────────

    async def get_customer_360(self, customer_id: uuid.UUID) -> Customer360Response:
        customer = await self._customers.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(context={"customer_id": str(customer_id)})

        conversations = await self._conversations.list_by_customer(customer_id)
        current = conversations[0] if conversations else None
        recent = conversations[:RECENT_CONVERSATIONS_LIMIT]

        avg_resolution = None
        resolved_durations = [
            (c.updated_at - c.created_at).total_seconds()
            for c in conversations
            if c.current_status in (ConversationStatus.RESOLVED, ConversationStatus.CLOSED)
        ]
        if resolved_durations:
            avg_resolution = sum(resolved_durations) / len(resolved_durations)

        escalation_count = sum(
            1 for c in conversations if c.current_status == ConversationStatus.ESCALATED
        )

        employee_name = None
        if current and current.assigned_employee_id:
            names = await self._resolve_employee_names({current.assigned_employee_id})
            employee_name = names.get(current.assigned_employee_id)

        open_complaints = await self._complaints.count_open_by_customer(customer_id)
        complaints = await self._complaints.get_by_customer_id(customer_id)

        latest_insight = await self._agent_assist.latest_for_customer(customer_id)

        return Customer360Response(
            customer=CustomerInfo(
                id=customer.id,
                customer_number=customer.customer_number,
                full_name=customer.full_name,
                email=customer.email,
                mobile_number=customer.mobile_number,
                segment=str(customer.segment),
                status=str(customer.status),
            ),
            current_conversation=(
                ConversationResponse.model_validate(current) if current is not None else None
            ),
            assigned_employee=(
                AssignedEmployee(id=current.assigned_employee_id, full_name=employee_name)
                if current and current.assigned_employee_id
                else None
            ),
            recent_conversations=[
                ConversationSummary(
                    id=c.id,
                    customer_id=c.customer_id,
                    complaint_id=c.complaint_id,
                    current_status=c.current_status,
                    current_channel=c.current_channel,
                    assigned_employee_id=c.assigned_employee_id,
                    priority=c.priority,
                    updated_at=c.updated_at,
                    customer_name=customer.full_name,
                    last_message_preview=None,
                )
                for c in recent
            ],
            conversation_statistics=ConversationStatistics(
                total_conversations=len(conversations),
                avg_resolution_seconds=avg_resolution,
                escalation_count=escalation_count,
            ),
            overview=CustomerOverview(
                open_complaints=open_complaints,
                conversation_count=len(conversations),
                avg_resolution_seconds=avg_resolution,
                escalation_count=escalation_count,
            ),
            agent_assist=(
                AgentAssistSnapshot(
                    summary=latest_insight.summary,
                    sentiment=latest_insight.sentiment,
                    intent=latest_insight.intent,
                    intent_confidence=latest_insight.intent_confidence,
                    generated_at=latest_insight.created_at,
                )
                if latest_insight is not None
                else None
            ),
            complaints=[
                _to_complaint_summary(c) for c in complaints[:RECENT_CONVERSATIONS_LIMIT]
            ],
        )

    async def get_customer_activity_timeline(
        self, customer_id: uuid.UUID, *, page: int = 1, page_size: int = 50
    ) -> CustomerActivityTimelineResponse:
        customer = await self._customers.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(context={"customer_id": str(customer_id)})

        conversations = await self._conversations.list_by_customer(customer_id)
        conversation_ids = [c.id for c in conversations]

        events, _ = await self._events.list_by_customer(customer_id, page=1, page_size=1000)
        messages = await self._messages.list_for_conversations(conversation_ids)

        items: list[TimelineItem] = [
            TimelineItem(
                type="message",
                id=m.id,
                timestamp=m.created_at,
                sender_type=m.sender_type,
                channel=m.channel,
                message_type=m.message_type,
                content=m.content,
                payload=m.message_metadata,
            )
            for m in messages
        ] + [
            TimelineItem(
                type="event",
                id=e.id,
                timestamp=e.created_at,
                event_type=e.event_type,
                source_domain=e.source_domain,
                payload=e.payload,
            )
            for e in events
        ]
        items.sort(key=lambda item: item.timestamp)

        total = len(items)
        offset = (page - 1) * page_size
        page_items = items[offset : offset + page_size]

        return CustomerActivityTimelineResponse(
            items=page_items, total=total, page=page, page_size=page_size
        )

    # ── Enterprise Analytics ─────────────────────────────────────────────

    async def get_conversation_summary(self, **filters) -> ConversationAnalyticsSummary:
        status_counts = await self._conversations.count_by_status(**filters)
        ai_vs_human = await self._conversations.count_ai_vs_human(**filters)
        avg_resolution = await self._conversations.avg_resolution_seconds(**filters)
        avg_duration = await self._conversations.avg_duration_seconds(**filters)

        handoff_rows = await self._events.list_by_event_type(
            _AI_HANDED_OVER, date_from=filters.get("date_from"), date_to=filters.get("date_to")
        )
        handoff_count = sum(
            1 for e in handoff_rows if (e.payload or {}).get("direction") == "ai_to_human"
        )

        conversation_ids = await self._conversations.list_ids(
            limit=MESSAGE_RESPONSE_TIME_CONVERSATION_CAP, **filters
        )
        avg_response = await self._avg_response_time_seconds(conversation_ids)

        total = sum(status_counts.values())
        active_statuses = {
            str(ConversationStatus.ACTIVE),
            str(ConversationStatus.AI_HANDLING),
            str(ConversationStatus.HUMAN_HANDLING),
            str(ConversationStatus.WAITING_FOR_AGENT),
            str(ConversationStatus.WAITING_FOR_CUSTOMER),
        }
        active = sum(count for status, count in status_counts.items() if status in active_statuses)
        resolved = status_counts.get(str(ConversationStatus.RESOLVED), 0) + status_counts.get(
            str(ConversationStatus.CLOSED), 0
        )
        escalated = status_counts.get(str(ConversationStatus.ESCALATED), 0)

        return ConversationAnalyticsSummary(
            total_conversations=total,
            active_conversations=active,
            resolved_conversations=resolved,
            escalated_conversations=escalated,
            ai_handled=ai_vs_human["ai_handled"],
            human_handled=ai_vs_human["human_handled"],
            ai_to_human_handoffs=handoff_count,
            avg_response_time_seconds=avg_response,
            avg_resolution_time_seconds=avg_resolution,
            avg_conversation_duration_seconds=avg_duration,
            customer_satisfaction=None,
        )

    async def _avg_response_time_seconds(
        self, conversation_ids: list[uuid.UUID]
    ) -> float | None:
        if not conversation_ids:
            return None
        messages = await self._messages.list_for_conversations(conversation_ids)
        by_conversation: dict[uuid.UUID, list] = defaultdict(list)
        for m in messages:
            by_conversation[m.conversation_id].append(m)

        deltas: list[float] = []
        for msgs in by_conversation.values():
            for prev, curr in zip(msgs, msgs[1:]):
                if str(prev.sender_type) == "customer" and str(curr.sender_type) != "customer":
                    deltas.append((curr.created_at - prev.created_at).total_seconds())
        return sum(deltas) / len(deltas) if deltas else None

    async def get_distributions(self, **filters) -> ConversationDistributions:
        channel_counts = await self._conversations.count_by_channel(**filters)
        complaint_counts = await self._complaints.count_by_category(
            date_from=filters.get("date_from"), date_to=filters.get("date_to")
        )
        insights = await self._agent_assist.latest_per_conversation(
            date_from=filters.get("date_from"), date_to=filters.get("date_to")
        )
        intent_counts = Counter(i.intent for i in insights if i.intent)
        sentiment_counts = Counter(i.sentiment for i in insights if i.sentiment)

        voice = channel_counts.get(str(ConversationChannel.VOICE), 0)
        total_channel = sum(channel_counts.values())
        return ConversationDistributions(
            intent_distribution=dict(intent_counts),
            sentiment_distribution=dict(sentiment_counts),
            complaint_distribution=complaint_counts,
            channel_distribution=channel_counts,
            voice_vs_chat=VoiceVsChat(voice=voice, chat=total_channel - voice),
        )

    async def get_trends(
        self,
        *,
        granularity: str = "day",
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> ConversationTrends:
        rows = await self._conversations.list_for_trends(
            limit=5000, date_from=date_from, date_to=date_to
        )

        bucket = _bucket_fn(granularity)
        conversation_trend: Counter[str] = Counter()
        ai_util: dict[str, dict[str, int]] = defaultdict(lambda: {"ai_handled": 0, "human_handled": 0})
        for conversation in rows:
            period = bucket(conversation.created_at)
            conversation_trend[period] += 1
            if conversation.ai_handling:
                ai_util[period]["ai_handled"] += 1
            if conversation.human_handling:
                ai_util[period]["human_handled"] += 1

        complaint_trend: Counter[str] = Counter()
        complaint_dates = await self._complaints.list_created_dates(
            date_from=date_from, date_to=date_to
        )
        for created_at in complaint_dates:
            complaint_trend[bucket(created_at)] += 1

        insights = await self._agent_assist.latest_per_conversation(
            date_from=date_from, date_to=date_to
        )
        sentiment_by_period: dict[str, Counter[str]] = defaultdict(Counter)
        intent_by_period: dict[str, Counter[str]] = defaultdict(Counter)
        for insight in insights:
            period = bucket(insight.created_at)
            if insight.sentiment:
                sentiment_by_period[period][insight.sentiment] += 1
            if insight.intent:
                intent_by_period[period][insight.intent] += 1

        periods = sorted(
            set(conversation_trend) | set(complaint_trend) | set(sentiment_by_period) | set(intent_by_period)
        )

        return ConversationTrends(
            granularity=granularity,
            conversation_trend=[TrendPoint(period=p, count=conversation_trend.get(p, 0)) for p in periods],
            complaint_trend=[TrendPoint(period=p, count=complaint_trend.get(p, 0)) for p in periods],
            sentiment_trend=[
                SentimentTrendPoint(
                    period=p,
                    positive=sentiment_by_period[p].get("positive", 0),
                    neutral=sentiment_by_period[p].get("neutral", 0),
                    frustrated=sentiment_by_period[p].get("frustrated", 0),
                    escalated=sentiment_by_period[p].get("escalated", 0),
                )
                for p in periods
            ],
            intent_trend=[IntentTrendPoint(period=p, counts=dict(intent_by_period[p])) for p in periods],
            ai_utilization_trend=[
                AiUtilizationTrendPoint(
                    period=p,
                    ai_handled=ai_util[p]["ai_handled"],
                    human_handled=ai_util[p]["human_handled"],
                )
                for p in periods
            ],
        )

    async def get_employee_analytics(self, **filters) -> list[EmployeeAnalyticsItem]:
        rows = await self._conversations.list_assigned(**filters)

        by_employee: dict[uuid.UUID, list] = defaultdict(list)
        for c in rows:
            by_employee[c.assigned_employee_id].append(c)

        ai_usage = await self._agent_assist.count_by_employee(
            date_from=filters.get("date_from"), date_to=filters.get("date_to")
        )
        transfer_rows = await self._events.list_by_event_type(
            _CONVERSATION_TRANSFERRED,
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
        )
        transfer_counts: Counter[str] = Counter()
        for e in transfer_rows:
            new_owner = (e.payload or {}).get("new_owner")
            if new_owner:
                transfer_counts[new_owner] += 1

        names = await self._resolve_employee_names(set(by_employee.keys()))

        items: list[EmployeeAnalyticsItem] = []
        for employee_id, convs in by_employee.items():
            resolved = [
                c for c in convs
                if c.current_status in (ConversationStatus.RESOLVED, ConversationStatus.CLOSED)
            ]
            escalated = sum(1 for c in convs if c.current_status == ConversationStatus.ESCALATED)
            avg_resolution = None
            if resolved:
                durations = [(c.updated_at - c.created_at).total_seconds() for c in resolved]
                avg_resolution = sum(durations) / len(durations)
            items.append(
                EmployeeAnalyticsItem(
                    employee_id=employee_id,
                    employee_name=names.get(employee_id),
                    assigned_conversations=len(convs),
                    resolved=len(resolved),
                    escalated=escalated,
                    avg_resolution_seconds=avg_resolution,
                    ai_assistance_usage=ai_usage.get(employee_id, 0),
                    transfer_count=transfer_counts.get(str(employee_id), 0),
                )
            )
        items.sort(key=lambda i: i.assigned_conversations, reverse=True)
        return items

    async def get_supervisor_dashboard(self) -> SupervisorDashboard:
        status_counts = await self._conversations.count_by_status()
        live_statuses = {
            str(ConversationStatus.ACTIVE),
            str(ConversationStatus.AI_HANDLING),
            str(ConversationStatus.HUMAN_HANDLING),
            str(ConversationStatus.WAITING_FOR_AGENT),
            str(ConversationStatus.WAITING_FOR_CUSTOMER),
        }
        live = sum(count for status, count in status_counts.items() if status in live_statuses)
        escalated = status_counts.get(str(ConversationStatus.ESCALATED), 0)

        ai_vs_human = await self._conversations.count_ai_vs_human()
        high_priority_complaints = await self._complaints.count_high_priority_open()
        employees_online = get_presence_registry().count_online_employees()

        return SupervisorDashboard(
            queue_by_status=status_counts,
            live_conversations=live,
            high_priority_complaints=high_priority_complaints,
            escalated_cases=escalated,
            ai_active_conversations=ai_vs_human["ai_handled"],
            employees_online=employees_online,
        )


def _to_complaint_summary(complaint) -> ComplaintSummary:
    return ComplaintSummary(
        id=complaint.id,
        complaint_number=complaint.complaint_number,
        title=complaint.title,
        category=complaint.category,
        priority=complaint.priority,
        severity=complaint.severity,
        status=complaint.status,
        assigned_queue=complaint.assigned_queue,
        created_at=complaint.created_at,
    )


def _bucket_fn(granularity: str):
    def _day(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    def _week(dt: datetime) -> str:
        iso = dt.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"

    def _month(dt: datetime) -> str:
        return dt.strftime("%Y-%m")

    return {"day": _day, "week": _week, "month": _month}.get(granularity, _day)
