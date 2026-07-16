"""Verify Scenarios — Programmatically runs the 5 business scenarios.

Run via:
    python scripts/verify_scenarios.py
"""

import asyncio
import os
import sys
import uuid
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.platform.database.session import init_db_engine, get_session_factory, close_db_engine
from domains.interaction.constants.interaction_constants import InteractionChannel
from domains.interaction.services.conversation_engine import process_conversation

async def run_scenario(name, customer_ref, channel, message):
    print(f"\n=========================================")
    print(f"RUNNING: {name}")
    print(f"Channel: {channel.value}, Message: '{message}'")
    print(f"=========================================")
    
    session_factory = get_session_factory()
    async with session_factory() as session:
        # Resolve services and repositories
        from domains.interaction.repositories.interaction_repository import InteractionRepository
        from domains.interaction.services.interaction_service import InteractionService
        from domains.customer.repositories.customer_repository import CustomerRepository
        from domains.complaint.repositories.complaint_repository import ComplaintRepository
        from domains.complaint.services.complaint_service import ComplaintService
        from domains.workflow.repositories.workflow_repository import WorkflowRepository
        from domains.workflow.services.workflow_service import WorkflowService
        from domains.notification.repositories.notification_repository import NotificationRepository
        from domains.notification.services.notification_service import NotificationService
        
        int_repo = InteractionRepository(session)
        int_service = InteractionService(int_repo)
        
        cust_repo = CustomerRepository(session)
        comp_repo = ComplaintRepository(session)
        comp_service = ComplaintService(
            repository=comp_repo,
            customer_repository=cust_repo,
            interaction_repository=int_repo,
        )
        
        wf_repo = WorkflowRepository(session)
        wf_service = WorkflowService(
            repository=wf_repo,
            complaint_repository=comp_repo,
        )
        
        notif_repo = NotificationRepository(session)
        notif_service = NotificationService(
            repository=notif_repo,
            workflow_repository=wf_repo,
        )
        
        from domains.interaction.schemas.interaction_schemas import InteractionCreate
        from domains.interaction.constants.interaction_constants import InteractionDirection, InteractionStatus
        
        data = InteractionCreate(
            customer_ref=customer_ref,
            channel=channel,
            direction=InteractionDirection.INBOUND,
            subject=f"Simulated {channel.value.capitalize()} Session",
            transcript="[]",
            status=InteractionStatus.RECEIVED,
        )
        interaction, _ = await int_service.create_interaction(data)
        await session.flush()
        
        interaction_id = interaction.id
        print(f"Created Interaction ID: {interaction_id}")
        
        # Process message
        result = await process_conversation(
            interaction_id=interaction_id,
            message=message,
            interaction_service=int_service,
            complaint_service=comp_service,
            workflow_service=wf_service,
            notification_service=notif_service,
        )
        await session.commit()
        
        print(f"AI Answer: {result['answer']}")
        print(f"Auto Triaged: {result['auto_triaged']}")
        print(f"Complaint ID: {result['complaint_id']}")
        print(f"Workflow ID: {result['workflow_id']}")
        
        # Let's query notifications if complaint created
        if result['complaint_id']:
            from domains.notification.models.notification import Notification
            from sqlalchemy import select
            stmt = select(Notification).where(Notification.complaint_id == uuid.UUID(result['complaint_id']))
            notifs = (await session.execute(stmt)).scalars().all()
            notif_ids = [str(n.id) for n in notifs]
            print(f"Notification IDs: {notif_ids}")
            result['notification_ids'] = notif_ids
        else:
            result['notification_ids'] = []
            
        return interaction_id, result

async def main():
    print("Bootstrapping application...")
    from app.startup.bootstrap import _init_prompts, _init_infrastructure
    _init_prompts()
    await _init_infrastructure()
    
    scenarios = [
        ("Scenario 1: Motor claim delayed", "cust-102", InteractionChannel.WEB_FORM, "My motor claim has been delayed."),
        ("Scenario 2: Refund request", "cust-102", InteractionChannel.EMAIL, "I need premium refund."),
        ("Scenario 3: Travel policy renewal", "cust-102", InteractionChannel.WHATSAPP, "I want to renew my travel policy."),
        ("Scenario 4: Medical reimbursement", "cust-102", InteractionChannel.VOICE, "My medical reimbursement hasn't arrived."),
        ("Scenario 5: Bad repair quality", "cust-102", InteractionChannel.WEB_FORM, "The garage repaired my car badly."),
    ]
    
    results = []
    for name, cust, chan, msg in scenarios:
        try:
            int_id, res = await run_scenario(name, cust, chan, msg)
            results.append({
                "scenario": name,
                "message": msg,
                "channel": chan.value,
                "interaction_id": str(int_id),
                "answer": res["answer"],
                "complaint_id": res["complaint_id"],
                "workflow_id": res["workflow_id"],
                "notification_ids": res["notification_ids"],
                "ai_analysis": {
                    "sentiment": res.get("ai_analysis", {}).get("sentiment", {}).get("sentiment") if res.get("ai_analysis", {}).get("sentiment") else None,
                    "severity": res.get("ai_analysis", {}).get("severity", {}).get("severity") if res.get("ai_analysis", {}).get("severity") else None,
                    "confidence": res.get("ai_analysis", {}).get("detection", {}).get("confidence") if res.get("ai_analysis", {}).get("detection") else None,
                    "primary_theme": res.get("ai_analysis", {}).get("themes", {}).get("primary_theme") if res.get("ai_analysis", {}).get("themes") else None,
                }
            })
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()
        
    with open("scenario_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\nSaved all scenario results to scenario_results.json")
    await close_db_engine()

if __name__ == "__main__":
    asyncio.run(main())
