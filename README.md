# AI-SIEM-SOAR

AI-assisted integrated SIEM/SOAR thesis platform.

Architecture: Wazuh provides the central SIEM/XDR layer. Suricata provides network IDS telemetry. Shuffle provides SOAR workflows and response automation. Ollama provides the local LLM runtime. This repository provides the custom AI analysis and integration module.

The AI module analyzes Wazuh alerts, produces structured incident assessments, selects approved Shuffle playbooks, and invokes integrations only through policy-controlled APIs. High-impact actions require human approval.

Four development agents now focus on integration, deployment, testing, and validation rather than rebuilding SIEM/SOAR products.

Target flow: Wazuh Agent and Suricata -> Wazuh -> AI Analysis Module -> policy gate -> Shuffle -> response.
