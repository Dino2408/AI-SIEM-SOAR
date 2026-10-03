#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
WAZUH_VERSION="${WAZUH_VERSION:-4.14.8}"
mkdir -p deploy
[[ -d deploy/wazuh ]] || git clone --depth 1 --branch "v$WAZUH_VERSION" https://github.com/wazuh/wazuh-docker.git deploy/wazuh
[[ -d deploy/shuffle ]] || git clone --depth 1 https://github.com/Shuffle/Shuffle.git deploy/shuffle
mkdir -p data/suricata
echo "Bootstrap complete."
