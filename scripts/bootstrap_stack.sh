#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
WAZUH_VERSION="\${WAZUH_VERSION:-4.14.8}"
SHUFFLE_REF="\${SHUFFLE_REF:-main}"
mkdir -p vendor
if [ ! -d vendor/wazuh-docker/.git ]; then
  git clone --depth 1 --branch "v$WAZUH_VERSION" https://github.com/wazuh/wazuh-docker.git vendor/wazuh-docker
fi
if [ ! -d vendor/Shuffle/.git ]; then
  git clone --depth 1 --branch "$SHUFFLE_REF" https://github.com/Shuffle/Shuffle.git vendor/Shuffle
fi
sudo sysctl -w vm.max_map_count=262144 >/dev/null || true
chmod +x scripts/*.sh docker/wazuh-ai-integration/*.sh docker/wazuh-ai-integration/custom-ai
cp -n .env.example .env 2>/dev/null || true
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d ai-analysis
cd vendor/wazuh-docker/single-node
if [ ! -f config/wazuh_indexer_ssl_certs/root-ca.pem ]; then
  docker compose -f generate-indexer-certs.yml run --rm generator
fi
docker compose -f docker-compose.yml -f ../../../docker/wazuh-ai-integration/compose.override.yml build wazuh.manager
docker compose -f docker-compose.yml -f ../../../docker/wazuh-ai-integration/compose.override.yml up -d
cd "$ROOT/vendor/Shuffle"
if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || true; fi
docker compose up -d
cd "$ROOT"
echo "Integrated stack started."
