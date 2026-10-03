# AI-SIEM-SOAR

AI-assisted integrated SIEM/SOAR thesis platform.

## Runtime architecture

- Wazuh: central SIEM/XDR, endpoint telemetry, decoding, rules and alerting.
- Suricata: network IDS and EVE JSON telemetry.
- AI Analysis Module: project-owned service that analyzes Wazuh alerts with a local LLM, builds source-backed evidence, applies deterministic policy, audits the decision and can invoke an approved Shuffle webhook.
- Ollama: local LLM runtime. Host Ollama is the default; a Docker GPU profile is available for compatible NVIDIA hosts.
- Shuffle: open-source SOAR workflow engine.
- Optional MISP/OpenCTI can be added later for threat-intelligence enrichment.

Target flow:

Suricata / Wazuh Agent -> Wazuh -> AI Analysis Module -> policy gate -> Shuffle -> approved response

## Docker-first deployment

The project does not reimplement Wazuh or Shuffle. The bootstrap script fetches the official Wazuh Docker single-node stack at v4.14.8 and the Shuffle on-prem stack, while the repository supplies the AI service, Suricata container, Wazuh custom integration overlay, tests and policy boundary.

Start on Ubuntu:

    cp .env.example .env
    chmod +x scripts/*.sh docker/wazuh-ai-integration/*
    ./scripts/ubuntu_bootstrap.sh

The first smoke test does not require an LLM. Without OLLAMA_MODEL the AI service returns BLOCKED instead of fabricating an analysis.

## Development agents

The four agents now build, deploy and validate the integrated stack:

1. Integration Architect
2. AI Integration Developer
3. Integration DevOps & Tester
4. SOC Manager & Validator

The Orchestrator is infrastructure, not a fifth agent.

## Safety

The LLM is a reasoning component, not an execution engine. Evidence is derived from the source Wazuh alert. Response names are allowlisted. High-impact actions such as host isolation and account disabling require human approval and are not autonomously executed by this module. All AI decisions are audited.

See docs/DOCKER_ARCHITECTURE.md and docs/UBUNTU_RUNBOOK.md for deployment details.
