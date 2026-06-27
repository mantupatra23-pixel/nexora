from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.services.executor_service import WorkflowExecutorEngine
from app.schemas.workflow import WorkflowExecuteRequest, WorkflowExecutionResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_workflow(
    workflow_id: UUID,
    payload: WorkflowExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = WorkflowRepository(db)
    engine = WorkflowExecutorEngine(repo)
    try:
        execution = await engine.execute(workflow_id, payload.input_data)
        return execution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution_status(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = WorkflowRepository(db)
    execution = await repo.get_execution_by_id(execution_id)
    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution log entries not found.")
    return execution
