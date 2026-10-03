# Deployment

Prepare a Linux Docker host, set vm.max_map_count to 262144, copy .env.example to .env, then run scripts/bootstrap.sh.

For Wazuh:
cd deploy/wazuh/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d

For the AI stack, from repository root:
docker compose up -d
docker exec -it ollama ollama pull qwen2.5-coder:7b

For Shuffle, configure deploy/shuffle and start its official compose deployment.

First end-to-end test:
Wazuh alert -> AI Gateway -> Ollama -> validated decision -> Shuffle playbook.
