import json
from typing import Dict, Any, List
from app.schemas.agent import AgentConfig
from app.services.ai_providers import AIProviderFactory

class AutonomousAgentOrchestrator:
    def __init__(self, config: AgentConfig, api_key: str):
        self.config = config
        self.api_key = api_key

    async def execute_autonomous_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Planning Engine - Task Decomposition
        planning_prompt = (
            "You are a master planning agent. Decompose the following task into sequential steps "
            "executable by internal scripts. Output the response strictly as a validated JSON list of strings."
        )
        user_query = f"Task to decompose: {task_description}\nContext data: {json.dumps(context)}"
        
        raw_plan = await AIProviderFactory.call_llm(
            provider=self.config.provider,
            model_name=self.config.model_name,
            temperature=0.1,
            system_prompt=planning_prompt,
            user_input=user_query,
            api_key=self.api_key
        )
        
        try:
            # Clean up potential markdown blocks if LLM outputs it
            clean_plan = raw_plan.replace("```json", "").replace("```", "").strip()
            steps: List[str] = json.loads(clean_plan)
        except Exception:
            steps = [task_description]  # Fallback to absolute raw task string execution

        # Step 2: Sequential Execution with Memory
        execution_history = []
        current_state_context = dict(context)

        for idx, step in enumerate(steps):
            agent_system_prompt = (
                f"Your Core Identity: {self.config.role}\n"
                f"Master Operational Guidelines: {self.config.system_prompt}\n"
                f"Execute step {idx+1}/{len(steps)}: {step}"
            )
            
            step_input = f"Current State Memory Context: {json.dumps(current_state_context)}\nHistory logs: {json.dumps(execution_history)}"
            
            step_output = await AIProviderFactory.call_llm(
                provider=self.config.provider,
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                system_prompt=agent_system_prompt,
                user_input=step_input,
                api_key=self.api_key
            )
            
            execution_history.append({"step": step, "output": step_output})
            current_state_context[f"step_{idx+1}_result"] = step_output

        # Step 3: Reflection Engine - Final Review and Verification
        reflection_prompt = (
            "Review the compiled answers from execution steps against the initial goal. "
            "Synthesize them into a highly optimized final production ready output response."
        )
        
        final_summary = await AIProviderFactory.call_llm(
            provider=self.config.provider,
            model_name=self.config.model_name,
            temperature=0.2,
            system_prompt=reflection_prompt,
            user_input=f"Goal: {task_description}\nExecution Chain Logs: {json.dumps(execution_history)}",
            api_key=self.api_key
        )

        return {
            "status": "success",
            "plan_steps": steps,
            "final_output": final_summary,
            "execution_metadata": execution_history
        }
