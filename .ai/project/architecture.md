# Architecture

User -> Orchestrator -> four fixed agents -> SIEM/SOAR product.

The Orchestrator manages workflow state, routing, model selection, permissions, artifacts and audit. The Tool Gateway exposes only allowlisted deterministic operations.

LLM = reasoning/decision. Tools = execution/verification. Evidence must be deterministic. Human retains final acceptance, main merge authority and approval for safety-critical SOAR actions.
