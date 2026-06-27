import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Workflow, WorkflowExecution
from typing import Optional, List

class WorkflowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workflow_by_id(self, workflow_id: uuid.UUID) -> Optional[Workflow]:
        result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalars().first()

    async def create_execution(self, execution: WorkflowExecution) -> WorkflowExecution:
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def update_execution(self, execution: WorkflowExecution) -> WorkflowExecution:
        await self.db.merge(execution)
        await self.db.commit()
        return execution

    async def get_execution_by_id(self, execution_id: uuid.UUID) -> Optional[WorkflowExecution]:
        result = await self.db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
        return result.scalars().first()
