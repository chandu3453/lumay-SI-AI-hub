"""Agent Assist service unit tests."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from domains.agent_assist.constants.agent_assist_constants import (
    AgentAssistAlertType,
    AgentAssistSentiment,
    MIN_MESSAGES_SINCE_LAST_REGEN,
    MIN_SECONDS_SINCE_LAST_REGEN,
)
from domains.agent_assist.services.agent_assist_service import (
    AgentAssistService,
    _SENTIMENT_MAP,
    _assemble_alerts,
    _to_response,
)


@pytest.fixture
async def service(mocker) -> AgentAssistService:
    mock_repo = mocker.AsyncMock()
    return AgentAssistService(repository=mock_repo)


@pytest.mark.asyncio
class TestShouldRegenerate:
    async def test_no_prior_insight_always_regenerates(self, service: AgentAssistService) -> None:
        service._repository.get_latest.return_value = None
        assert await service.should_regenerate(uuid.uuid4(), message_count=1) is True

    async def test_enough_new_messages_regenerates(self, service: AgentAssistService, mocker) -> None:
        service._repository.get_latest.return_value = mocker.Mock(
            message_count_at_generation=5, created_at=datetime.now(UTC)
        )
        message_count = 5 + MIN_MESSAGES_SINCE_LAST_REGEN
        assert await service.should_regenerate(uuid.uuid4(), message_count=message_count) is True

    async def test_too_few_messages_and_too_soon_does_not_regenerate(
        self, service: AgentAssistService, mocker,
    ) -> None:
        service._repository.get_latest.return_value = mocker.Mock(
            message_count_at_generation=5, created_at=datetime.now(UTC)
        )
        assert await service.should_regenerate(uuid.uuid4(), message_count=6) is False

    async def test_enough_time_elapsed_regenerates_even_with_one_new_message(
        self, service: AgentAssistService, mocker,
    ) -> None:
        stale_time = datetime.now(UTC) - timedelta(seconds=MIN_SECONDS_SINCE_LAST_REGEN + 5)
        service._repository.get_latest.return_value = mocker.Mock(
            message_count_at_generation=5, created_at=stale_time
        )
        assert await service.should_regenerate(uuid.uuid4(), message_count=6) is True


class TestSentimentMapping:
    def test_positive_variants_map_to_positive(self) -> None:
        assert _SENTIMENT_MAP["very_positive"] == AgentAssistSentiment.POSITIVE
        assert _SENTIMENT_MAP["positive"] == AgentAssistSentiment.POSITIVE

    def test_negative_maps_to_frustrated_not_escalated(self) -> None:
        assert _SENTIMENT_MAP["negative"] == AgentAssistSentiment.FRUSTRATED

    def test_very_negative_maps_to_escalated(self) -> None:
        assert _SENTIMENT_MAP["very_negative"] == AgentAssistSentiment.ESCALATED

    def test_neutral_maps_to_neutral(self) -> None:
        assert _SENTIMENT_MAP["neutral"] == AgentAssistSentiment.NEUTRAL


class TestAssembleAlerts:
    def test_sentiment_crossing_into_frustrated_raises_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.FRUSTRATED,
            previous_sentiment=AgentAssistSentiment.NEUTRAL,
            escalation_risk_score=10,
            missing_info=[],
            complaint_severity=None,
            previous_complaint_severity=None,
        )
        assert any(a["type"] == AgentAssistAlertType.FRUSTRATION_INCREASING for a in alerts)

    def test_already_frustrated_does_not_re_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.FRUSTRATED,
            previous_sentiment=AgentAssistSentiment.FRUSTRATED,
            escalation_risk_score=10,
            missing_info=[],
            complaint_severity=None,
            previous_complaint_severity=None,
        )
        assert not any(a["type"] == AgentAssistAlertType.FRUSTRATION_INCREASING for a in alerts)

    def test_high_escalation_risk_raises_escalation_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.NEUTRAL,
            previous_sentiment=AgentAssistSentiment.NEUTRAL,
            escalation_risk_score=85,
            missing_info=[],
            complaint_severity=None,
            previous_complaint_severity=None,
        )
        assert any(a["type"] == AgentAssistAlertType.ESCALATION_RECOMMENDED for a in alerts)
        assert any(a["severity"] == "critical" for a in alerts)

    def test_low_escalation_risk_raises_no_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.NEUTRAL,
            previous_sentiment=AgentAssistSentiment.NEUTRAL,
            escalation_risk_score=5,
            missing_info=[],
            complaint_severity=None,
            previous_complaint_severity=None,
        )
        assert not any(a["type"] == AgentAssistAlertType.ESCALATION_RECOMMENDED for a in alerts)
        assert not any(a["type"] == AgentAssistAlertType.URGENT for a in alerts)

    def test_missing_info_raises_documents_missing_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.NEUTRAL,
            previous_sentiment=AgentAssistSentiment.NEUTRAL,
            escalation_risk_score=0,
            missing_info=["policy number"],
            complaint_severity=None,
            previous_complaint_severity=None,
        )
        assert any(a["type"] == AgentAssistAlertType.DOCUMENTS_MISSING for a in alerts)

    def test_complaint_severity_change_raises_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.NEUTRAL,
            previous_sentiment=AgentAssistSentiment.NEUTRAL,
            escalation_risk_score=0,
            missing_info=[],
            complaint_severity="critical",
            previous_complaint_severity="low",
        )
        assert any(a["type"] == AgentAssistAlertType.COMPLAINT_SEVERITY_CHANGED for a in alerts)

    def test_unchanged_complaint_severity_raises_no_alert(self) -> None:
        alerts = _assemble_alerts(
            sentiment=AgentAssistSentiment.NEUTRAL,
            previous_sentiment=AgentAssistSentiment.NEUTRAL,
            escalation_risk_score=0,
            missing_info=[],
            complaint_severity="low",
            previous_complaint_severity="low",
        )
        assert not any(a["type"] == AgentAssistAlertType.COMPLAINT_SEVERITY_CHANGED for a in alerts)


class TestToResponse:
    def test_stalled_flag_true_when_inactive_past_threshold(self, mocker) -> None:
        conversation = mocker.Mock(
            created_at=datetime.now(UTC) - timedelta(minutes=30),
            updated_at=datetime.now(UTC) - timedelta(minutes=15),
            current_status="active",
        )
        insight = mocker.Mock(
            id=uuid.uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            conversation_id=uuid.uuid4(),
            message_count_at_generation=3,
            summary=None,
            intent=None,
            intent_confidence=None,
            sentiment=None,
            sentiment_polarity=None,
            escalation_risk_score=None,
            escalation_risk_level=None,
            next_best_actions=None,
            knowledge_articles=None,
            suggested_replies=None,
            insights=None,
            alerts=None,
            complaint_severity_at_generation=None,
        )
        response = _to_response(insight, conversation)
        assert response.stalled is True
        assert any(a.type == AgentAssistAlertType.CONVERSATION_STALLED for a in response.alerts)

    def test_not_stalled_when_recently_active(self, mocker) -> None:
        conversation = mocker.Mock(
            created_at=datetime.now(UTC) - timedelta(minutes=5),
            updated_at=datetime.now(UTC),
            current_status="active",
        )
        insight = mocker.Mock(
            id=uuid.uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            conversation_id=uuid.uuid4(),
            message_count_at_generation=1,
            summary=None,
            intent=None,
            intent_confidence=None,
            sentiment=None,
            sentiment_polarity=None,
            escalation_risk_score=None,
            escalation_risk_level=None,
            next_best_actions=None,
            knowledge_articles=None,
            suggested_replies=None,
            insights=None,
            alerts=None,
            complaint_severity_at_generation=None,
        )
        response = _to_response(insight, conversation)
        assert response.stalled is False

    def test_closed_conversation_never_reports_stalled(self, mocker) -> None:
        conversation = mocker.Mock(
            created_at=datetime.now(UTC) - timedelta(hours=2),
            updated_at=datetime.now(UTC) - timedelta(hours=1),
            current_status="closed",
        )
        insight = mocker.Mock(
            id=uuid.uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            conversation_id=uuid.uuid4(),
            message_count_at_generation=1,
            summary=None,
            intent=None,
            intent_confidence=None,
            sentiment=None,
            sentiment_polarity=None,
            escalation_risk_score=None,
            escalation_risk_level=None,
            next_best_actions=None,
            knowledge_articles=None,
            suggested_replies=None,
            insights=None,
            alerts=None,
            complaint_severity_at_generation=None,
        )
        response = _to_response(insight, conversation)
        assert response.stalled is False
