# AI-SIEM-SOAR

AI-augmented open-source SIEM/SOAR MVP.

Core components: Wazuh, Suricata, AI Gateway, Ollama and Shuffle.

The AI layer never executes arbitrary shell commands. It emits a validated decision consumed by an approved Shuffle playbook.

This branch establishes the Docker and AI foundation. Wazuh and Shuffle are consumed from their upstream deployment repositories instead of copying large vendor-managed trees into this repository.

Run:
1. cp .env.example .env
2. bash scripts/bootstrap.sh
3. bash scripts/start.sh
