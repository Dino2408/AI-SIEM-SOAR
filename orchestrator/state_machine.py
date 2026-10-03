from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowState(str, Enum):
    INIT = "INIT"
    REQUIREMENTS_ANALYSIS = "REQUIREMENTS_ANALYSIS"
    ARCHITECTURE = "ARCHITECTURE"
    TASK_PLANNING = "TASK_PLANNING"
    DEVELOPMENT = "DEVELOPMENT"
    DEVOPS_BUILD = "DEVOPS_BUILD"
    TESTING = "TESTING"
    VALIDATION = "VALIDATION"
    CREATE_DEFECT = "CREATE_DEFECT"
    ROUTE_DEFECT = "ROUTE_DEFECT"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    FINAL_ACCEPTANCE = "FINAL_ACCEPTANCE"
    PRODUCT_COMPLETE = "PRODUCT_COMPLETE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class AgentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    BLOCKED = "BLOCKED"


class ValidationResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


class DefectCategory(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    REQUIREMENT = "REQUIREMENT"
    CODE = "CODE"
    DEVOPS = "DEVOPS"
    TEST = "TEST"
    UNKNOWN = "UNKNOWN"


class TransitionError(ValueError):
    """Raised when a workflow transition violates the state contract."""


LEGAL_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.INIT: {WorkflowState.REQUIREMENTS_ANALYSIS},
    WorkflowState.REQUIREMENTS_ANALYSIS: {
        WorkflowState.ARCHITECTURE,
        WorkflowState.HUMAN_REVIEW,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.ARCHITECTURE: {
        WorkflowState.TASK_PLANNING,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.TASK_PLANNING: {
        WorkflowState.DEVELOPMENT,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.DEVELOPMENT: {
        WorkflowState.DEVOPS_BUILD,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.DEVOPS_BUILD: {
        WorkflowState.TESTING,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.TESTING: {
        WorkflowState.VALIDATION,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.VALIDATION: {
        WorkflowState.CREATE_DEFECT,
        WorkflowState.FINAL_ACCEPTANCE,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.CREATE_DEFECT: {
        WorkflowState.ROUTE_DEFECT,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.ROUTE_DEFECT: {
        WorkflowState.ARCHITECTURE,
        WorkflowState.DEVELOPMENT,
        WorkflowState.DEVOPS_BUILD,
        WorkflowState.TESTING,
        WorkflowState.HUMAN_REVIEW,
        WorkflowState.BLOCKED,
        WorkflowState.FAILED,
    },
    WorkflowState.HUMAN_REVIEW: {
        WorkflowState.REQUIREMENTS_ANALYSIS,
        WorkflowState.ARCHITECTURE,
        WorkflowState.BLOCKED,
    },
    WorkflowState.FINAL_ACCEPTANCE: {
        WorkflowState.PRODUCT_COMPLETE,
        WorkflowState.VALIDATION,
        WorkflowState.BLOCKED,
    },
    WorkflowState.PRODUCT_COMPLETE: set(),
    WorkflowState.BLOCKED: set(),
    WorkflowState.FAILED: set(),
}


@dataclass
class WorkflowContext:
    workflow_id: str
    state: WorkflowState = WorkflowState.INIT
    previous_state: WorkflowState | None = None
    iteration: int = 0
    fix_iteration: int = 0
    active_task_id: str | None = None
    last_agent: str | None = None
    last_status: AgentStatus | None = None
    validation_result: ValidationResult | None = None
    pending_defects: list[dict[str, Any]] = field(default_factory=list)
    human_approved: bool = False
    human_decision: str | None = None


class StateMachine:
    def __init__(self, max_fix_iterations: int = 3) -> None:
        if max_fix_iterations < 1:
            raise ValueError("max_fix_iterations must be >= 1")
        self.max_fix_iterations = max_fix_iterations

    def can_transition(
        self, current: WorkflowState, target: WorkflowState
    ) -> bool:
        return target in LEGAL_TRANSITIONS.get(current, set())

    def transition(
        self,
        context: WorkflowContext,
        target: WorkflowState,
        *,
        validation_result: ValidationResult | None = None,
        human_approved: bool = False,
        human_decision: str | None = None,
    ) -> WorkflowContext:
        if not self.can_transition(context.state, target):
            raise TransitionError(
                f"Illegal transition: {context.state.value} -> {target.value}"
            )

        if target == WorkflowState.FINAL_ACCEPTANCE:
            if validation_result != ValidationResult.PASS:
                raise TransitionError(
                    "FINAL_ACCEPTANCE requires explicit Validator PASS"
                )

        if target == WorkflowState.PRODUCT_COMPLETE:
            if not context.human_approved:
                raise TransitionError(
                    "PRODUCT_COMPLETE requires explicit human acceptance"
                )

        if target in {
            WorkflowState.ARCHITECTURE,
            WorkflowState.DEVELOPMENT,
            WorkflowState.DEVOPS_BUILD,
            WorkflowState.TESTING,
        } and context.state == WorkflowState.ROUTE_DEFECT:
            if context.fix_iteration >= self.max_fix_iterations:
                context.state = WorkflowState.BLOCKED
                raise TransitionError(
                    "Maximum fix iterations reached; human intervention required"
                )
            context.fix_iteration += 1

        context.previous_state = context.state
        context.state = target
        context.iteration += 1

        if validation_result is not None:
            context.validation_result = validation_result
        if human_approved:
            context.human_approved = True
        if human_decision is not None:
            context.human_decision = human_decision

        return context

    def route_defect(self, category: DefectCategory) -> WorkflowState:
        return {
            DefectCategory.ARCHITECTURE: WorkflowState.ARCHITECTURE,
            DefectCategory.REQUIREMENT: WorkflowState.HUMAN_REVIEW,
            DefectCategory.CODE: WorkflowState.DEVELOPMENT,
            DefectCategory.DEVOPS: WorkflowState.DEVOPS_BUILD,
            DefectCategory.TEST: WorkflowState.TESTING,
            DefectCategory.UNKNOWN: WorkflowState.HUMAN_REVIEW,
        }[category]
