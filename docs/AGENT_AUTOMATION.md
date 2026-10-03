# Four-Agent Automation Runtime

The repository contains an executable four-agent workflow.

Roles:
1. Architect — requirements, architecture and build plan.
2. Developer — product source, tests and Docker artifacts.
3. DevOps/Tester — deterministic local execution and evidence.
4. Validator — evidence-based quality gate.

The Orchestrator is infrastructure, not a fifth agent. It owns state transitions, permissions, artifact boundaries, audit logging and human gates.

The active LLM is selected by the CLI. One model is invoked at a time. Agent identity is a policy/profile, not a separate model.

The LLM returns a strict JSON envelope. The runtime validates it, writes only allowed artifacts and routes tool calls through ToolGateway.

On Ubuntu:
./scripts/run_agent_workflow.sh <installed-ollama-model>

The workflow stops at FINAL_ACCEPTANCE after Validator PASS. Human acceptance is still required.

Agents cannot write Git internals, merge main, run arbitrary shells, execute production actions or fabricate evidence.
