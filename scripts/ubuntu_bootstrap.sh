#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
command -v git >/dev/null || { echo "git is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker Engine is required"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose v2 is required"; exit 1; }
mkdir -p .ai/audit data
cp -n .env.example .env 2>/dev/null || true
chmod +x scripts/*.sh docker/wazuh-ai-integration/*.sh docker/wazuh-ai-integration/custom-ai
./scripts/bootstrap_stack.sh
./scripts/stack_smoke_test.sh
