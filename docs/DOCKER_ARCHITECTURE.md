# Docker architecture

The repository uses Docker as the deployment boundary for the project-owned services and preserves the upstream container topology for Wazuh and Shuffle.

## Containers

1. Wazuh indexer — upstream Wazuh single-node image.
2. Wazuh manager — upstream image rebuilt with the project custom Integrator adapter.
3. Wazuh dashboard — upstream image.
4. Suricata — passive NIDS container using host networking.
5. AI Analysis Module — project-owned Python service.
6. Shuffle backend/frontend/orborus/database — upstream Shuffle Compose stack.
7. Optional Ollama — Docker GPU profile. The default deployment uses host Ollama because the thesis machine has a single 8 GB GPU and model/runtime compatibility should be benchmarked before moving inference into Docker.

## Persistent data

Wazuh's upstream Compose volumes persist its indexer, manager and dashboard state. The project creates persistent volumes for AI audit records and Suricata EVE logs.

## Network boundaries

The project Compose stack creates the external Docker network ai-siem-soar-soc. The Wazuh manager joins it so its custom Integrator can reach the AI module by service name. The AI module reaches Shuffle through the configured webhook URL.

## Security boundary

The LLM never receives a shell tool. Its response is treated as untrusted data. The AI service constructs evidence from the source alert, bounds the playbook name to an allowlist, and rejects autonomous high-impact actions. The only outbound automation path is the configured Shuffle webhook.

## Deployment model

scripts/bootstrap_stack.sh:

- creates the shared network and volumes;
- fetches pinned Wazuh Docker v4.14.8;
- fetches Shuffle;
- generates Wazuh certificates;
- builds the custom Wazuh manager overlay;
- starts Wazuh, Suricata, AI and Shuffle.

This avoids maintaining a forked copy of large upstream Wazuh and Shuffle Compose definitions.
