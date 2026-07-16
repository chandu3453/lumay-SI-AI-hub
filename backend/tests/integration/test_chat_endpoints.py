"""AI Chat Endpoints Integration Tests."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from ai.models import ChatResponse, ChatMessage, TokenUsage, AIResponse
from ai.intelligence.models import (
    ComplaintAnalysis,
    ComplaintDetection,
    SentimentAnalysis,
    ThemeAnalysis,
    SeverityPrediction,
    EscalationRiskAssessment,
    PriorityRecommendation,
    ComplaintSummary,
    RootCauseAnalysis,
    ResolutionRecommendation,
    LanguageDetection,
    AnalysisMetadata,
)


@pytest.mark.asyncio
class TestChatEndpoints:
    """End-to-end integration tests for Sprint 16 chat router endpoints."""

    async def test_chat_lifecycle_api(self, client: AsyncClient) -> None:
        # 1. Start Chat Session
        start_resp = await client.post(
            "/api/v1/interactions/chat/start",
            json={
                "customer_ref": "cust-test-101",
                "channel": "whatsapp",
            },
        )
        assert start_resp.status_code == 201
        res_data = start_resp.json()["data"]
        interaction_id = res_data["id"]
        assert interaction_id is not None
        assert res_data["channel"] == "whatsapp"
        assert res_data["status"] == "received"

        # 2. Retrieve history and assert our new chat session is listed
        history_resp = await client.get("/api/v1/interactions/chat/history")
        assert history_resp.status_code == 200
        history_items = history_resp.json()["data"]
        assert len(history_items) > 0
        ids = [item["id"] for item in history_items]
        assert interaction_id in ids

        # Mock AI Response and Analysis to bypass external API dependency
        mock_chat_response = ChatResponse(
            message=ChatMessage(role="assistant", content="I will escalate your claim review."),
            finish_reason="stop",
            model="gpt-mock",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=10, latency_ms=10.0),
        )

        mock_generate_response = AIResponse(
            content="Mocked RAG knowledge answer.",
            finish_reason="stop",
            model="gpt-mock",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=10, latency_ms=10.0),
        )

        meta = AnalysisMetadata(model_used="mock", processing_time_ms=1.0)
        mock_analysis = ComplaintAnalysis(
            detection=ComplaintDetection(is_complaint=True, detection_type="definite", confidence=0.95, primary_complaint_statement="Escalate review", excerpt="Escalate review", detected_language="en", explanation="", evidence=[], metadata=meta),
            sentiment=SentimentAnalysis(sentiment="very_negative", sentiment_start="neutral", sentiment_end="very_negative", sentiment_trend="declining", polarity=-0.9, emotions={"anger": 0.8}, intensity=0.9, sentiment_target="claim_process", confidence=0.9, explanation="", evidence=[], metadata=meta),
            themes=ThemeAnalysis(primary_theme="claims", subcategory="delay", confidence=0.95, explanation="", evidence=[], metadata=meta),
            severity=SeverityPrediction(severity="critical", confidence=0.95, explanation="", evidence=[], auto_escalation_triggers=[], metadata=meta),
            escalation=EscalationRiskAssessment(escalation_risk_score=90.0, confidence=0.9, explanation="", evidence=[], metadata=meta),
            priority=PriorityRecommendation(priority="high", sla_risk="at_risk", confidence=0.9, explanation="", evidence=[], metadata=meta),
            summary=ComplaintSummary(summary="Customer claims review is delayed.", metadata=meta),
            root_cause=RootCauseAnalysis(root_cause="Process delay", process_failure_point="Surveyor check", recommended_fix="", prevention_suggestion="", confidence=0.9, explanation="", evidence=[], metadata=meta),
            resolution=ResolutionRecommendation(recommended_action="Escalate check", steps=[], department="claims", routing_rule="", escalation_required=True, estimated_resolution_time="", suggested_response_template="", confidence=0.9, explanation="", evidence=[], metadata=meta),
            language=LanguageDetection(detected_language="en", language_confidence=1.0, script="latin", metadata=meta),
            metadata=meta,
        )

        with patch("ai.gateway.ai_gateway.AIGateway.chat", new_callable=AsyncMock) as mock_chat, \
             patch("ai.gateway.ai_gateway.AIGateway.generate", new_callable=AsyncMock) as mock_generate, \
             patch("ai.intelligence.service.ComplaintIntelligenceService.analyze_complete", new_callable=AsyncMock) as mock_analyze:
            mock_chat.return_value = mock_chat_response
            mock_generate.return_value = mock_generate_response
            mock_analyze.return_value = mock_analysis

            # 3. Send message and trigger AI RAG generation
            message_resp = await client.post(
                "/api/v1/interactions/chat/message",
                json={
                    "interaction_id": interaction_id,
                    "message": "Can you please escalate my motor claim review immediately?",
                },
            )
            print("MESSAGE ERROR RESP:", message_resp.json())
            assert message_resp.status_code == 200
            message_data = message_resp.json()["data"]
            assert message_data["answer"] == "I will escalate your claim review."
            assert len(message_data["messages"]) >= 2
            assert "ai_analysis" in message_data
            assert message_data["auto_triaged"] is True
            assert message_data["complaint_id"] is not None

        # 4. Get conversation messages details
        get_conv_resp = await client.get(f"/api/v1/interactions/chat/{interaction_id}")
        assert get_conv_resp.status_code == 200
        conv_messages = get_conv_resp.json()["data"]
        assert len(conv_messages) >= 2
        assert conv_messages[0]["role"] == "user"
        assert conv_messages[1]["role"] == "assistant"

        # 5. End Session
        end_resp = await client.post(
            "/api/v1/interactions/chat/end",
            json={
                "interaction_id": interaction_id,
                "message": "Done",
            },
        )
        assert end_resp.status_code == 200
        assert end_resp.json()["data"]["status"] == "completed"

    async def test_omnichannel_conversations_api(self, client: AsyncClient) -> None:
        customer_ref_uuid = "00000000-0000-0000-0000-000000000202"
        # 1. Start Conversation via new endpoint
        start_resp = await client.post(
            "/api/v1/interactions/conversations/start",
            json={
                "customer_ref": customer_ref_uuid,
                "channel": "email",
            },
        )
        assert start_resp.status_code == 201
        res_data = start_resp.json()["data"]
        interaction_id = res_data["id"]
        assert interaction_id is not None
        assert res_data["channel"] == "email"

        # 2. List all conversations via new endpoint
        list_resp = await client.get("/api/v1/interactions/conversations")
        assert list_resp.status_code == 200
        items = list_resp.json()["data"]
        assert len(items) > 0

        # Mock AI Response and Analysis to bypass external API dependency
        mock_chat_response = ChatResponse(
            message=ChatMessage(role="assistant", content="We will resolve this."),
            finish_reason="stop",
            model="gpt-mock",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=10, latency_ms=10.0),
        )

        mock_generate_response = AIResponse(
            content="Mocked RAG knowledge answer.",
            finish_reason="stop",
            model="gpt-mock",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=10, latency_ms=10.0),
        )

        meta = AnalysisMetadata(model_used="mock", processing_time_ms=1.0)
        mock_analysis = ComplaintAnalysis(
            detection=ComplaintDetection(is_complaint=False, detection_type="none", confidence=0.1, primary_complaint_statement="", excerpt="", detected_language="en", explanation="", evidence=[], metadata=meta),
            sentiment=SentimentAnalysis(sentiment="neutral", sentiment_start="neutral", sentiment_end="neutral", sentiment_trend="stable", polarity=0.0, emotions={"joy": 0.5}, intensity=0.1, sentiment_target="", confidence=0.9, explanation="", evidence=[], metadata=meta),
            themes=ThemeAnalysis(primary_theme="general", subcategory="inquiry", confidence=0.95, explanation="", evidence=[], metadata=meta),
            severity=SeverityPrediction(severity="moderate", confidence=0.95, explanation="", evidence=[], auto_escalation_triggers=[], metadata=meta),
            escalation=EscalationRiskAssessment(escalation_risk_score=10.0, confidence=0.9, explanation="", evidence=[], metadata=meta),
            priority=PriorityRecommendation(priority="medium", sla_risk="on_track", confidence=0.9, explanation="", evidence=[], metadata=meta),
            summary=ComplaintSummary(summary="General inquiry", metadata=meta),
            root_cause=RootCauseAnalysis(root_cause="Inquiry", process_failure_point="", recommended_fix="", prevention_suggestion="", confidence=0.9, explanation="", evidence=[], metadata=meta),
            resolution=ResolutionRecommendation(recommended_action="", steps=[], department="service", routing_rule="", escalation_required=False, estimated_resolution_time="", suggested_response_template="", confidence=0.9, explanation="", evidence=[], metadata=meta),
            language=LanguageDetection(detected_language="en", language_confidence=1.0, script="latin", metadata=meta),
            metadata=meta,
        )

        with patch("ai.gateway.ai_gateway.AIGateway.chat", new_callable=AsyncMock) as mock_chat, \
             patch("ai.gateway.ai_gateway.AIGateway.generate", new_callable=AsyncMock) as mock_generate, \
             patch("ai.intelligence.service.ComplaintIntelligenceService.analyze_complete", new_callable=AsyncMock) as mock_analyze:
            mock_chat.return_value = mock_chat_response
            mock_generate.return_value = mock_generate_response
            mock_analyze.return_value = mock_analysis

            # 3. Post a message to conversation via new message endpoint
            msg_resp = await client.post(
                "/api/v1/interactions/conversations/message",
                json={
                    "interaction_id": interaction_id,
                    "message": "Hi, I have a quick question about policy renewals.",
                },
            )
            assert msg_resp.status_code == 200
            msg_data = msg_resp.json()["data"]
            assert msg_data["answer"] == "We will resolve this."

            # 4. Process a voice turn via new voice process endpoint
            voice_resp = await client.post(
                "/api/v1/interactions/voice/process",
                json={
                    "interaction_id": interaction_id,
                    "message": "Verify garage approval status.",
                },
            )
            assert voice_resp.status_code == 200
            assert voice_resp.json()["data"]["answer"] == "We will resolve this."

            # 5. Process an email turn via new email process endpoint
            email_resp = await client.post(
                "/api/v1/interactions/email/process",
                json={
                    "interaction_id": interaction_id,
                    "message": "Please send cancellation details.",
                },
            )
            assert email_resp.status_code == 200

            # 6. Process a WhatsApp turn via new WhatsApp process endpoint
            wa_resp = await client.post(
                "/api/v1/interactions/whatsapp/process",
                json={
                    "interaction_id": interaction_id,
                    "message": "Need road assistance location.",
                },
            )
            assert wa_resp.status_code == 200

        # 7. Get conversation details by ID
        conv_resp = await client.get(f"/api/v1/interactions/conversations/{interaction_id}")
        assert conv_resp.status_code == 200

        # 8. Get customer history
        cust_hist_resp = await client.get(f"/api/v1/interactions/customer/{customer_ref_uuid}/history")
        assert cust_hist_resp.status_code == 200
        assert len(cust_hist_resp.json()["data"]) > 0

        # 9. End active conversation
        end_resp = await client.post(
            "/api/v1/interactions/conversations/end",
            json={
                "interaction_id": interaction_id,
                "message": "Goodbye",
            },
        )
        assert end_resp.status_code == 200
