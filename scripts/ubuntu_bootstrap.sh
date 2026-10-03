#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
command -v git >/dev/null || { echo "git is required"; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose v2 is required"; exit 1; }
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p .ai/audit data
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml ps
echo "SIEM/SOAR bootstrap completed."
echo "Health: curl http://127.0.0.1:8080/health"
