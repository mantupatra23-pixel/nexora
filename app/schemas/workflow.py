from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime

class NodeData(BaseModel):
    node_type: str = Field(..., alias="type")  # e.g., 'trigger', 'webhook', 'ai_agent', 'condition'
    parameters: Dict[str, Any] = Field(default_factory=dict)

class WorkflowNode(BaseModel):
    id: str
    data: NodeData

class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    source_handle: Optional[str] = Field(default=None, alias="sourceHandle")

class WorkflowExecuteRequest(BaseModel):
    input_data: Dict[str, Any] = Field(default_factory=dict)

class WorkflowExecutionResponse(BaseModel):
    execution_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
