"""Test create_session directly."""
import asyncio
import sys
sys.path.insert(0, ".")

from voice.session_manager import SessionManager


async def test():
    from app.platform.database.session import get_session
    from domains.interaction.services.interaction_service import InteractionService
    from domains.complaint.services.complaint_service import ComplaintService
    from domains.workflow.services.workflow_service import WorkflowService
    from domains.notification.services.notification_service import NotificationService
    from app.repositories.interaction_repository import InteractionRepository
    from app.repositories.complaint_repository import ComplaintRepository
    from app.repositories.workflow_repository import WorkflowRepository
    from app.repositories.notification_repository import NotificationRepository

    async with get_session() as db:
        sm = SessionManager(
            interaction_service=InteractionService(InteractionRepository(db)),
            complaint_service=ComplaintService(ComplaintRepository(db)),
            workflow_service=WorkflowService(WorkflowRepository(db)),
            notification_service=NotificationService(NotificationRepository(db)),
        )
        try:
            result = await asyncio.wait_for(sm.create_session(), timeout=10)
            print(f"SUCCESS: session_id={result['session_id']}")
        except asyncio.TimeoutError:
            print("TIMEOUT - create_session hung")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")


asyncio.run(test())
