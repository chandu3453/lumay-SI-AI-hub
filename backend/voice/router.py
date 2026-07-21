"""Voice REST API — unified entry point for the voice pipeline.

Endpoints:
    POST /voice/token        – Get LiveKit token + create session
    POST /voice/start        – Start session + Pipecat pipeline
    POST /voice/end          – End session + cleanup
    GET  /voice/sessions/{id} – Session status
    GET  /voice/sessions/{id}/transcript – Transcript segments
    GET  /voice/sessions/{id}/stream    – SSE transcript stream
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.interaction import get_interaction_service
from app.dependencies.complaint import get_complaint_service
from app.dependencies.workflow import get_workflow_service
from app.dependencies.notification import get_notification_service
from app.platform.logging import get_logger
from shared.base_schema import AppBaseModel
from shared.response_schemas import SuccessResponse
from voice.session_manager import SessionManager
from voice.transcript_manager import get_transcript_manager
from voice.runtime import VoiceRuntime

router = APIRouter(prefix="/voice", tags=["Voice"])
logger = get_logger(__name__)


# ── Schemas ────────────────────────────────────────────────────────

class VoiceTokenRequest(AppBaseModel):
    customer_ref: str | None = None
    room_name: str | None = None


class VoiceTokenResponse(AppBaseModel):
    session_id: str
    interaction_id: str
    room_name: str
    participant_token: str
    livekit_url: str


class VoiceEndRequest(AppBaseModel):
    session_id: str


class VoiceEndResponse(AppBaseModel):
    session_id: str
    status: str
    transcript: list[dict[str, Any]] = []


class TranscriptSegmentSchema(AppBaseModel):
    role: str
    text: str
    is_partial: bool = False
    timestamp: str


class VoiceSessionStatusResponse(AppBaseModel):
    session_id: str
    interaction_id: str
    room_name: str
    status: str
    transcript_segments: list[TranscriptSegmentSchema] = []
    started_at: str | None = None
    ended_at: str | None = None


# ── Factory ─────────────────────────────────────────────────────────

async def get_session_manager(
    interaction_service=Depends(get_interaction_service),
    complaint_service=Depends(get_complaint_service),
    workflow_service=Depends(get_workflow_service),
    notification_service=Depends(get_notification_service),
) -> SessionManager:
    return SessionManager(
        interaction_service=interaction_service,
        complaint_service=complaint_service,
        workflow_service=workflow_service,
        notification_service=notification_service,
    )


# ── Endpoints ───────────────────────────────────────────────────────

@router.post(
    "/token",
    response_model=SuccessResponse[VoiceTokenResponse],
    summary="Get LiveKit token",
)
async def get_voice_token(
    body: VoiceTokenRequest,
    sm: SessionManager = Depends(get_session_manager),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[VoiceTokenResponse]:
    result = await sm.create_session(
        customer_ref=body.customer_ref,
        room_name=body.room_name,
    )
    return SuccessResponse(data=VoiceTokenResponse(
        session_id=result["session_id"],
        interaction_id=result["interaction_id"],
        room_name=result["room_name"],
        participant_token=result["participant_token"],
        livekit_url=result["livekit_url"],
    ))


@router.post(
    "/start",
    response_model=SuccessResponse[VoiceTokenResponse],
    summary="Start voice session + Pipecat pipeline",
)
async def start_voice_session(
    body: VoiceTokenRequest,
    sm: SessionManager = Depends(get_session_manager),
) -> SuccessResponse[VoiceTokenResponse]:
    result = await sm.create_session(
        customer_ref=body.customer_ref,
        room_name=body.room_name,
    )

    import asyncio
    asyncio.create_task(_run_pipeline_isolated(
        session_id=result["session_id"],
        room_name=result["room_name"],
        agent_token=result["agent_token"],
        interaction_id=result["interaction_id"],
    ))

    return SuccessResponse(data=VoiceTokenResponse(
        session_id=result["session_id"],
        interaction_id=result["interaction_id"],
        room_name=result["room_name"],
        participant_token=result["participant_token"],
        livekit_url=result["livekit_url"],
    ))


async def _run_pipeline_isolated(
    session_id: str,
    room_name: str,
    agent_token: str,
    interaction_id: str,
) -> None:
    """Run pipeline with its own DB session to avoid sharing with request."""
    from app.platform.database.session import get_session_factory
    from domains.interaction.services.interaction_service import InteractionService
    from domains.complaint.services.complaint_service import ComplaintService
    from domains.workflow.services.workflow_service import WorkflowService
    from domains.notification.services.notification_service import NotificationService
    from domains.interaction.repositories.interaction_repository import InteractionRepository
    from domains.complaint.repositories.complaint_repository import ComplaintRepository
    from domains.workflow.repositories.workflow_repository import WorkflowRepository
    from domains.notification.repositories.notification_repository import NotificationRepository
    from domains.customer.repositories.customer_repository import CustomerRepository

    try:
        factory = get_session_factory()
        async with factory() as db:
            repo_interaction = InteractionRepository(db)
            repo_complaint = ComplaintRepository(db)
            repo_workflow = WorkflowRepository(db)
            repo_notification = NotificationRepository(db)
            repo_customer = CustomerRepository(db)

            interaction_service = InteractionService(repo_interaction)
            complaint_service = ComplaintService(
                repo_complaint,
                customer_repository=repo_customer,
                interaction_repository=repo_interaction,
            )
            workflow_service = WorkflowService(
                repo_workflow,
                complaint_repository=repo_complaint,
            )
            notification_service = NotificationService(
                repo_notification,
                workflow_repository=repo_workflow,
            )
            try:
                await VoiceRuntime.start_pipeline(
                    session_id=session_id,
                    room_name=room_name,
                    agent_token=agent_token,
                    interaction_id=interaction_id,
                    stt_provider=None,
                    tts_provider=None,
                    interaction_service=interaction_service,
                    complaint_service=complaint_service,
                    workflow_service=workflow_service,
                    notification_service=notification_service,
                )
            finally:
                # This session is held open for the whole call (every turn's
                # transcript/complaint write only flushes, per
                # InteractionRepository/ComplaintRepository) — without this,
                # everything is silently rolled back when the `async with
                # factory()` block below closes, and the voice transcript
                # never reaches Postgres regardless of how the call ended.
                await db.commit()
    except Exception:
        logger = get_logger(__name__)
        logger.exception("pipeline_background_failed", session_id=session_id)


@router.post(
    "/end",
    response_model=SuccessResponse[VoiceEndResponse],
    summary="End voice session",
)
async def end_voice_session(
    body: VoiceEndRequest,
    sm: SessionManager = Depends(get_session_manager),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[VoiceEndResponse]:
    result = await sm.end_session(body.session_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {body.session_id} not found",
        )
    return SuccessResponse(data=VoiceEndResponse(**result))


@router.get(
    "/sessions/{session_id}",
    response_model=SuccessResponse[VoiceSessionStatusResponse],
    summary="Get session status",
)
async def get_session_status(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[VoiceSessionStatusResponse]:
    session = await sm.get_session_status(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    segments = [
        TranscriptSegmentSchema(**seg)
        for seg in session.get("transcript_segments", [])
    ]
    return SuccessResponse(data=VoiceSessionStatusResponse(
        session_id=session["session_id"],
        interaction_id=session["interaction_id"],
        room_name=session["room_name"],
        status=session["status"],
        transcript_segments=segments,
        started_at=session.get("started_at"),
        ended_at=session.get("ended_at"),
    ))


@router.get(
    "/sessions/{session_id}/transcript",
    response_model=SuccessResponse[list[TranscriptSegmentSchema]],
    summary="Get session transcript",
)
async def get_session_transcript(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[TranscriptSegmentSchema]]:
    transcript = await sm.get_transcript(session_id)
    segments = [TranscriptSegmentSchema(**seg) for seg in transcript]
    return SuccessResponse(data=segments)


@router.get(
    "/sessions/{session_id}/stream",
    summary="Stream transcript via SSE",
)
async def stream_session_transcript(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> EventSourceResponse:
    import asyncio

    async def event_generator():
        last_index = 0
        while True:
            tm = get_transcript_manager()
            session = tm.get_session(session_id)
            if not session:
                yield {"event": "end", "data": "Session ended"}
                break

            segments = session.get("transcript_segments", [])
            if len(segments) > last_index:
                new_segments = segments[last_index:]
                last_index = len(segments)
                for seg in new_segments:
                    yield {"event": "transcript", "data": seg}

            if session.get("status") in ("ended", "error"):
                yield {"event": "end", "data": session.get("status", "ended")}
                break

            await asyncio.sleep(0.3)

    return EventSourceResponse(event_generator())
