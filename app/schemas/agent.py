from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class AgentConfig(BaseModel):
    name: str = Field(..., example="Copywriter Agent")
    role: str = Field(..., example="Expert Marketing Strategist")
    provider: str = Field(..., example="openai")  # openai, gemini, anthropic
    model_name: str = Field(..., example="gpt-4o")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    system_prompt: str = Field(..., example="You are a professional system reviewer...")

class AgentTaskPayload(BaseModel):
    task_description: str
    context_data: Dict[str, Any] = Field(default_factory=dict)
