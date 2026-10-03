import pytest

from orchestrator.router import WorkflowRouter
from orchestrator.state_machine import (
    AgentStatus,
    DefectCategory,
    StateMachine,
    TransitionError,
    ValidationResult,
    WorkflowContext,
    WorkflowState,
)


def build_context(state: WorkflowState = WorkflowState.INIT) -> WorkflowContext:
    return WorkflowContext(workflow_id="WF-TEST", state=state)


def test_main_path_transitions() -> None:
    sm = StateMachine()
    ctx = build_context()

    for target in (
        WorkflowState.REQUIREMENTS_ANALYSIS,
        WorkflowState.ARCHITECTURE,
        WorkflowState.TASK_PLANNING,
        WorkflowState.DEVELOPMENT,
        WorkflowState.DEVOPS_BUILD,
        WorkflowState.TESTING,
        WorkflowState.VALIDATION,
    ):
        sm.transition(ctx, target)

    sm.transition(
        ctx,
        WorkflowState.FINAL_ACCEPTANCE,
        validation_result=ValidationResult.PASS,
    )
    ctx.human_approved = True
    sm.transition(ctx, WorkflowState.PRODUCT_COMPLETE)

    assert ctx.state == WorkflowState.PRODUCT_COMPLETE


def test_illegal_transition_is_rejected() -> None:
    sm = StateMachine()
    ctx = build_context()

    with pytest.raises(TransitionError):
        sm.transition(ctx, WorkflowState.DEVELOPMENT)


def test_validation_fail_routes_to_defect() -> None:
    sm = StateMachine()
    ctx = build_context(WorkflowState.VALIDATION)

    router = WorkflowRouter(sm)
    assert router.route_validation(ctx, "FAIL") == WorkflowState.CREATE_DEFECT


def test_validation_blocked_routes_to_blocked() -> None:
    sm = StateMachine()
    ctx = build_context(WorkflowState.VALIDATION)

    router = WorkflowRouter(sm)
    assert router.route_validation(ctx, "BLOCKED") == WorkflowState.BLOCKED


def test_defect_routing() -> None:
    sm = StateMachine()
    router = WorkflowRouter(sm)

    assert router.route_defect("CODE") == WorkflowState.DEVELOPMENT
    assert router.route_defect("DEVOPS") == WorkflowState.DEVOPS_BUILD
    assert router.route_defect("TEST") == WorkflowState.TESTING
    assert router.route_defect("ARCHITECTURE") == WorkflowState.ARCHITECTURE
    assert router.route_defect("REQUIREMENT") == WorkflowState.HUMAN_REVIEW


def test_fix_iteration_limit() -> None:
    sm = StateMachine(max_fix_iterations=1)
    ctx = build_context(WorkflowState.ROUTE_DEFECT)

    sm.transition(ctx, WorkflowState.DEVELOPMENT)
    assert ctx.fix_iteration == 1

    ctx.state = WorkflowState.ROUTE_DEFECT
    with pytest.raises(TransitionError):
        sm.transition(ctx, WorkflowState.DEVELOPMENT)
    assert ctx.state == WorkflowState.BLOCKED


def test_product_complete_requires_human_acceptance() -> None:
    sm = StateMachine()
    ctx = build_context(WorkflowState.FINAL_ACCEPTANCE)

    with pytest.raises(TransitionError):
        sm.transition(ctx, WorkflowState.PRODUCT_COMPLETE)


def test_agent_status_enum_is_distinct_from_validation_result() -> None:
    assert AgentStatus.SUCCESS.value == "SUCCESS"
    assert ValidationResult.PASS.value == "PASS"
    assert AgentStatus.SUCCESS.value != ValidationResult.PASS.value


def test_all_defect_categories_are_mapped() -> None:
    sm = StateMachine()
    for category in DefectCategory:
        assert sm.route_defect(category) is not None
