#!/usr/bin/env bash
set -euo pipefail
AI_URL="http://127.0.0.1:\${AI_PORT:-8080}"
curl -fsS "$AI_URL/health" >/dev/null
curl -fsS -X POST "$AI_URL/v1/analyze" -H 'Content-Type: application/json' -d @tests/fixtures/wazuh-alert.json | python3 -m json.tool
if [ -d vendor/wazuh-docker/single-node ]; then
  docker compose -f vendor/wazuh-docker/single-node/docker-compose.yml -f docker/wazuh-ai-integration/compose.override.yml ps
fi
if [ -d vendor/Shuffle ]; then
  docker compose -f vendor/Shuffle/docker-compose.yml ps
fi
echo "Integrated stack smoke test completed."
