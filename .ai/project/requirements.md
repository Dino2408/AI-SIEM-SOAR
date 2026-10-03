# AI-SIEM-SOAR Product Requirements

## Objective
Build one local SIEM/SOAR product for the thesis: AI-assisted analysis and automated response to information-security events.

## Core capabilities
1. Collect security events from files and HTTP first; keep adapters extensible for Wazuh, Suricata and other vendors.
2. Parse heterogeneous logs through deterministic parsers and a parser registry.
3. Normalize events into one internal schema compatible in spirit with OCSF/ECS concepts.
4. Detect security conditions with deterministic rules before optional LLM reasoning.
5. Correlate related events into incidents.
6. Store and query events and alerts locally.
7. Execute SOAR playbooks through policy gates. Lab/dry-run actions are allowed; production-sensitive actions require human approval.
8. Expose a local API for health, event ingestion, event queries, alerts and safe playbook execution.
9. Provide tests, Docker packaging and repeatable local deployment.
10. Integrate four agents: Architect, Developer, DevOps/Tester, Validator.

## Non-goals
- No autonomous continuous self-rewriting.
- No uncontrolled shell access.
- No direct production response actions.
- No agent may merge main or approve its own validation.
- One active LLM model at a time.

## Acceptance
Human owner performs final acceptance after Validator PASS.
