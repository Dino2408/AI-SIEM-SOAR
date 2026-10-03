#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
docker compose -f docker/docker-compose.yml down
if [ -d vendor/wazuh-docker/single-node ]; then
  docker compose -f vendor/wazuh-docker/single-node/docker-compose.yml -f docker/wazuh-ai-integration/compose.override.yml down
fi
if [ -d vendor/Shuffle ]; then
  docker compose -f vendor/Shuffle/docker-compose.yml down
fi
