#!/usr/bin/env bash
set -euo pipefail
curl --fail --silent http://127.0.0.1:8080/health
echo
curl --fail --silent -X POST http://127.0.0.1:8080/api/v1/events -H 'Content-Type: application/json' -d '{"source":"smoke-test","event_type":"authentication","action":"login_failed","src_ip":"192.0.2.10","username":"lab-user"}'
echo
curl --fail --silent http://127.0.0.1:8080/api/v1/events
echo
