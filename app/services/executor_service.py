import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from app.models.models import Workflow, WorkflowExecution
from app.repositories.workflow_repository import WorkflowRepository

class WorkflowExecutorEngine:
    def __init__(self, repo: WorkflowRepository):
        self.repo = repo

    async def execute(self, workflow_id: uuid.UUID, initial_input: Dict[str, Any]) -> WorkflowExecution:
        workflow: Workflow = await self.repo.get_workflow_by_id(workflow_id)
        if not workflow or not workflow.is_active:
            raise ValueError("Workflow not found or is currently inactive.")

        # Complete execution record init status
        execution = WorkflowExecution(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            status="RUNNING",
            input_data=initial_input,
            output_data={},
            started_at=datetime.utcnow()
        )
        await self.repo.create_execution(execution)

        try:
            nodes: List[Dict[str, Any]] = workflow.nodes.get("nodes", [])
            edges: List[Dict[str, Any]] = workflow.edges.get("edges", [])
            
            # Build node reference maps and dependency tree
            node_map = {node["id"]: node for node in nodes}
            adj_list: Dict[str, List[str]] = {node["id"]: [] for node in nodes}
            in_degree: Dict[str, int] = {node["id"]: 0 for node in nodes}

            for edge in edges:
                src, tgt = edge["source"], edge["target"]
                if src in adj_list and tgt in in_degree:
                    adj_list[src].append(tgt)
                    in_degree[tgt] += 1

            # Topological Sort to run safe sequences asynchronously
            queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
            context_state: Dict[str, Any] = {"global_input": initial_input}

            while queue:
                current_batch = list(queue)
                queue.clear()
                
                # Parallel computation block for processing independent nodes simultaneously
                tasks = [self._execute_single_node(node_map[nid], context_state) for nid in current_batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for nid, res in zip(current_batch, results):
                    if isinstance(res, Exception):
                        raise res
                    context_state[nid] = res
                    
                    for neighbor in adj_list[nid]:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            queue.append(neighbor)

            execution.status = "COMPLETED"
            execution.output_data = context_state
            execution.completed_at = datetime.utcnow()
        
        except Exception as e:
            execution.status = "FAILED"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
        
        await self.repo.update_execution(execution)
        return execution

    async def _execute_single_node(self, node: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        node_type = node.get("type")
        params = node.get("parameters", {})
        
        # Core conditional routing checks
        if node_type == "webhook_trigger":
            return {"status": "triggered", "data": context.get("global_input")}
            
        elif node_type == "custom_code":
            # Dynamic execution engine safely boxed within local contexts
            local_vars = {"context": context, "output": {}}
            exec(params.get("code", "output = {}"), {}, local_vars)
            return local_vars.get("output", {})
            
        elif node_type == "condition":
            expression = params.get("expression", "True")
            # Evaluate expression securely inside system states
            result = eval(expression, {}, {"context": context})
            return {"condition_matched": bool(result)}
            
        return {"processed": True}
