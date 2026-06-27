from fastapi import APIRouter, Depends, HTTPException, Header, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.services.executor_service import WorkflowExecutorEngine
from app.schemas.integration import WebhookPayload

router = APIRouter(prefix="/v1/webhooks", tags=["Webhook Gateway"])

async def background_workflow_runner(workflow_id: UUID, initial_data: dict, db: AsyncSession):
    repo = WorkflowRepository(db)
    engine = WorkflowExecutorEngine(repo)
    try:
        await engine.execute(workflow_id, initial_data)
    except Exception as e:
        # Internal async logging state handles
        print(f"Async Background Webhook Trigger Failed: {str(e)}")

@router.post("/{workflow_id}/catch", status_code=status.HTTP_202_ACCEPTED)
async def catch_incoming_webhook(
    workflow_id: UUID,
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Non-blocking async event loops to answer source instantly within 50ms
    background_tasks.add_task(background_workflow_runner, workflow_id, payload.model_dump(), db)
    return {"status": "event_queued", "workflow_id": workflow_id}
