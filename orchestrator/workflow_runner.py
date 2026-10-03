from pathlib import Path
import json
import os
from .agent_manager import AgentManager
from .agent_runtime import AgentRuntime
from .audit_logger import AuditLogger
from .local_tools import build_default_registry
from .ollama_adapter import OllamaAdapter
from .permission_manager import PermissionManager
from .state_manager import StateManager
from .state_machine import StateMachine, WorkflowContext, WorkflowState, AgentStatus, ValidationResult
from .tool_gateway import ToolGateway

class WorkflowRunner:
    """Finite four-agent runner. Agents never control state transitions."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state_manager = StateManager(self.root / ".ai/state/workflow.json")
        self.audit = AuditLogger(self.root / ".ai/audit")
        self.agents = AgentManager(self.root / "agents")
        self.gateway = ToolGateway(build_default_registry(), self.audit, PermissionManager())
        self.ollama = OllamaAdapter(os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
        self.runtime = AgentRuntime(self.root, self.gateway, self.audit, self.ollama)
        self.sm = StateMachine(3)

    def _context(self):
        d = self.state_manager.load()
        return WorkflowContext(
            workflow_id=d["workflow_id"],
            state=WorkflowState(d["state"]),
            previous_state=WorkflowState(d["previous_state"]) if d.get("previous_state") else None,
            iteration=d.get("iteration", 0),
            fix_iteration=d.get("fix_iteration", 0),
            active_task_id=d.get("active_task_id"),
            last_agent=d.get("last_agent"),
            last_status=AgentStatus(d["last_status"]) if d.get("last_status") else None,
            validation_result=ValidationResult(d["validation_result"]) if d.get("validation_result") else None,
            pending_defects=d.get("pending_defects", []),
            human_approved=d.get("human_approved", False),
            human_decision=d.get("human_decision"),
        )

    def _save(self, c):
        self.state_manager.save({
            "workflow_id": c.workflow_id,
            "state": c.state.value,
            "previous_state": c.previous_state.value if c.previous_state else None,
            "iteration": c.iteration,
            "fix_iteration": c.fix_iteration,
            "active_task_id": c.active_task_id,
            "last_agent": c.last_agent,
            "last_status": c.last_status.value if c.last_status else None,
            "validation_result": c.validation_result.value if c.validation_result else None,
            "pending_defects": c.pending_defects,
            "human_approved": c.human_approved,
            "human_decision": c.human_decision,
            "limits": {"max_fix_iterations": 3},
        })

    def run(self, model):
        c = self._context()
        if c.state == WorkflowState.INIT:
            c = self.sm.transition(c, WorkflowState.REQUIREMENTS_ANALYSIS)
            self._save(c)

        if c.state == WorkflowState.FINAL_ACCEPTANCE:
            return {"status": "WAITING_HUMAN_ACCEPTANCE", "message": "Validator PASS; human acceptance required."}
        if c.state in {WorkflowState.PRODUCT_COMPLETE, WorkflowState.BLOCKED, WorkflowState.FAILED}:
            return {"status": c.state.value}

        phases = {
            WorkflowState.REQUIREMENTS_ANALYSIS: (WorkflowState.ARCHITECTURE, "architect"),
            WorkflowState.ARCHITECTURE: (WorkflowState.TASK_PLANNING, "architect"),
            WorkflowState.TASK_PLANNING: (WorkflowState.DEVELOPMENT, "developer"),
            WorkflowState.DEVELOPMENT: (WorkflowState.DEVOPS_BUILD, "devops"),
            WorkflowState.DEVOPS_BUILD: (WorkflowState.TESTING, "devops"),
            WorkflowState.TESTING: (WorkflowState.VALIDATION, "validator"),
        }

        while c.state in phases:
            target, agent = phases[c.state]
            c = self.sm.transition(c, target)
            c.last_agent = agent
            self._save(c)
            task = f"Execute workflow phase {target.value}. Read all relevant repository artifacts and complete your role contract."
            context = self.state_manager.load()
            result = self.runtime.run(agent, task, model, context)
            c.last_status = AgentStatus(result["status"])
            self._save(c)

            if result["status"] != "SUCCESS":
                if agent == "validator":
                    c.pending_defects.append({
                        "category": result.get("defect_category", "UNKNOWN"),
                        "summary": result["summary"],
                    })
                    c = self.sm.transition(c, WorkflowState.CREATE_DEFECT)
                    c = self.sm.transition(c, WorkflowState.ROUTE_DEFECT)
                    target = self.sm.route_defect(result.get("defect_category", "UNKNOWN"))
                    if c.fix_iteration >= 3:
                        c.state = WorkflowState.BLOCKED
                        self._save(c)
                        return result
                    c = self.sm.transition(c, target)
                    self._save(c)
                    return result
                c.state = WorkflowState.BLOCKED
                self._save(c)
                return result

        if c.state == WorkflowState.VALIDATION:
            c.validation_result = ValidationResult.PASS
            c = self.sm.transition(c, WorkflowState.FINAL_ACCEPTANCE, validation_result=ValidationResult.PASS)
            self._save(c)
            return {"status": "WAITING_HUMAN_ACCEPTANCE", "state": c.state.value}
        return {"status": c.state.value}
