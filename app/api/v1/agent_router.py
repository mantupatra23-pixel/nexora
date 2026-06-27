from fastapi import APIRouter, HTTPException, Header, status
from app.schemas.agent import AgentConfig, AgentTaskPayload
from app.services.agent_orchestrator import AutonomousAgentOrchestrator

router = APIRouter(prefix="/agents", tags=["AI Agents"])

@router.post("/run-autonomous-task", status_code=status.HTTP_200_OK)
async def run_agent_task(
    config: AgentConfig,
    payload: AgentTaskPayload,
    x_ai_api_key: str = Header(..., description="API Secret key for the chosen LLM provider (OpenAI / Gemini / Anthropic)")
):
    try:
        orchestrator = AutonomousAgentOrchestrator(config=config, api_key=x_ai_api_key)
        result = await orchestrator.execute_autonomous_task(
            task_description=payload.task_description,
            context=payload.context_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
