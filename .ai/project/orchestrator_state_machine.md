# Orchestrator State Machine Specification 1.0

## 1. Purpose

This specification defines the deterministic workflow controller for the AI-SIEM-SOAR development team.

The Orchestrator is infrastructure, not an AI agent. It controls state transitions, validates agent outputs, routes work, enforces limits, records audit events, and stops at human-approval gates.

## 2. Core principles

1. Agent != Model.
2. Only one LLM model is active at a time.
3. The state machine is deterministic; an LLM cannot choose or bypass workflow transitions.
4. LLMs provide reasoning and decisions; tools perform execution and verification.
5. Evidence must originate from deterministic tools.
6. Validator PASS requires sufficient evidence.
7. Human authority is retained for requirement gaps, safety-sensitive actions, main-branch merge, and final acceptance.
8. Feedback loops are bounded by `max_fix_iterations`.

## 3. Workflow states

| State | Owner | Purpose |
|---|---|---|
| INIT | Orchestrator | Initialize workflow context |
| REQUIREMENTS_ANALYSIS | Architect | Analyze requirements and constraints |
| ARCHITECTURE | Architect | Produce system architecture |
| TASK_PLANNING | Architect | Create executable development tasks |
| DEVELOPMENT | Developer | Implement source/test changes |
| DEVOPS_BUILD | DevOps | Build/package the product |
| TESTING | DevOps | Execute functional/detection tests and collect evidence |
| VALIDATION | Validator | Evaluate implementation against requirements |
| CREATE_DEFECT | Orchestrator | Persist validation defects |
| ROUTE_DEFECT | Orchestrator | Select responsible agent |
| HUMAN_REVIEW | Human | Resolve requirement/safety decisions |
| FINAL_ACCEPTANCE | Human | Accept the completed product |
| PRODUCT_COMPLETE | Orchestrator | Terminal successful state |
| BLOCKED | Orchestrator | Terminal/interruption state requiring intervention |
| FAILED | Orchestrator | Terminal workflow failure |

## 4. Agent execution status

Agent execution status is separate from workflow state:

- SUCCESS: requested work completed and output contract is valid.
- FAILURE: execution failed and may be retryable/routable.
- BLOCKED: agent cannot safely continue without external/human input.

A successful agent execution does not automatically mean product validation PASS.

## 5. Validator result

Only the Validator may produce:

- PASS
- FAIL
- BLOCKED

PASS requires evidence-based acceptance. Insufficient or invalid evidence results in BLOCKED.

## 6. Legal transitions

### Main path

`INIT -> REQUIREMENTS_ANALYSIS -> ARCHITECTURE -> TASK_PLANNING -> DEVELOPMENT -> DEVOPS_BUILD -> TESTING -> VALIDATION`

`VALIDATION(PASS) -> FINAL_ACCEPTANCE -> PRODUCT_COMPLETE`

### Defect path

`VALIDATION(FAIL) -> CREATE_DEFECT -> ROUTE_DEFECT`

Routing:

- ARCHITECTURE -> ARCHITECTURE
- REQUIREMENT -> HUMAN_REVIEW
- CODE -> DEVELOPMENT
- DEVOPS -> DEVOPS_BUILD
- TEST -> TESTING
- UNKNOWN -> HUMAN_REVIEW

After a routed fix:

`DEVELOPMENT -> DEVOPS_BUILD -> TESTING -> VALIDATION`

`DEVOPS_BUILD -> TESTING -> VALIDATION`

`TESTING -> VALIDATION`

### Blocked/error path

Any agent returning BLOCKED -> BLOCKED.

Retryable execution failure is retried by the Orchestrator until the configured failure limit is reached. After the limit, -> FAILED.

HUMAN_REVIEW may return to REQUIREMENTS_ANALYSIS or ARCHITECTURE after the user resolves the issue.

FINAL_ACCEPTANCE may return to VALIDATION if the human requests more evidence.

## 7. Transition guards

The Orchestrator MUST reject transitions when:

- the target state is not legal from the current state;
- required artifacts are missing;
- agent output fails its schema;
- the agent is not authorized for the target state;
- the fix-iteration limit has been reached;
- a human gate is required but no human decision exists.

For a validation PASS, the validation report and required evidence must exist.

For PRODUCT_COMPLETE, the Validator must have PASS and the human must have accepted the product.

## 8. Bounded feedback

Default limits:

- max_fix_iterations: 3
- max_format_retries: 2
- max_tool_failures: 3
- max_agent_turns: 20

A new defect-fix cycle increments `fix_iteration`. Once the maximum is reached, the workflow becomes BLOCKED and requires human intervention rather than silently looping.

## 9. Human gates

Human intervention is mandatory for:

1. unresolved requirement ambiguity;
2. safety-sensitive SOAR action approval;
3. final acceptance;
4. any workflow blocked by iteration/tool/agent limits.

The Orchestrator must never infer a human approval.

## 10. Defect routing

| Defect category | Route |
|---|---|
| ARCHITECTURE | ARCHITECTURE |
| REQUIREMENT | HUMAN_REVIEW |
| CODE | DEVELOPMENT |
| DEVOPS | DEVOPS_BUILD |
| TEST | TESTING |
| UNKNOWN | HUMAN_REVIEW |

## 11. State persistence

The state manager must persist at least:

- workflow_id
- current_state
- previous_state
- iteration
- fix_iteration
- active_task_id
- last_agent
- last_status
- validation_result
- pending_defects
- timestamps
- audit references

State persistence must be external to the LLM context so workflow control survives model changes or process restarts.

## 12. Security boundary

The Orchestrator never exposes arbitrary shell execution to agents. Agents invoke registered tools through the Tool Gateway.

The LLM cannot:

- directly modify workflow state;
- bypass permission checks;
- fabricate evidence;
- merge into `main`;
- approve its own validation;
- execute unrestricted SOAR actions.

## 13. Acceptance criteria

A Phase A1 implementation is complete when:

- all legal transitions are represented;
- illegal transitions raise a deterministic error;
- PASS/FAIL/BLOCKED validation routing works;
- defect categories route deterministically;
- fix iterations are bounded;
- human gates are enforced;
- state can be serialized and restored;
- unit tests cover the main path and failure paths.
