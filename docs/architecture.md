# MVP Architecture

Wazuh or Suricata -> AI Gateway -> Ollama -> schema validation -> policy validation -> approved Shuffle playbook -> controlled response.

The LLM has no Docker socket, SSH credentials or direct execution interface.

The AI Gateway is read-only and uses no-new-privileges.

Only allowlisted playbooks can be automated. High-risk and critical cases require human approval.

Wazuh and Shuffle are consumed from upstream deployment repositories so vendor-managed configuration is not duplicated here.
