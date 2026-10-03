from __future__ import annotations

from .state_machine import (
    DefectCategory,
    StateMachine,
    WorkflowContext,
    WorkflowState,
)


class WorkflowRouter:
    """Deterministic routing layer; agents cannot choose their next workflow state."""

    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine

    def route_validation(
        self, context: WorkflowContext, result: str
    ) -> WorkflowState:
        normalized = result.upper()
        if normalized == "PASS":
            return WorkflowState.FINAL_ACCEPTANCE
        if normalized == "FAIL":
            return WorkflowState.CREATE_DEFECT
        if normalized == "BLOCKED":
            return WorkflowState.BLOCKED
        raise ValueError(f"Unknown validation result: {result}")

    def route_defect(self, category: str) -> WorkflowState:
        try:
            return self.state_machine.route_defect(
                DefectCategory(category.upper())
            )
        except ValueError as exc:
            raise ValueError(f"Unknown defect category: {category}") from exc
