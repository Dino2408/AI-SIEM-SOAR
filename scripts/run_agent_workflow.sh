#!/usr/bin/env bash
set -euo pipefail
MODEL="${1:-}"
if [[ -z "$MODEL" ]]; then
  echo "Usage: ./scripts/run_agent_workflow.sh <ollama-model>"
  exit 2
fi
python3 -m orchestrator.cli agent-run --model "$MODEL"
