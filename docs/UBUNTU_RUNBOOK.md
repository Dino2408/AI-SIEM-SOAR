# Ubuntu Runbook

## Prerequisites
Ubuntu Server, Python 3.10+, Git, Docker Engine and Docker Compose v2.

Ollama is installed separately on the host. The repository does not hard-code a model.

## Bootstrap
Run:
chmod +x scripts/ubuntu_bootstrap.sh scripts/ubuntu_smoke_test.sh scripts/ubuntu_stop.sh
./scripts/ubuntu_bootstrap.sh

## Smoke test
Run:
./scripts/ubuntu_smoke_test.sh

## Inspect
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs --tail=100 siem-api
curl http://127.0.0.1:8080/health

The API binds to 127.0.0.1:8080 and is not exposed to the LAN by default.

## Product direction
The executable foundation is:
collector -> parser -> normalizer -> detection -> correlation -> alert -> SOAR.

The placeholder modules will be replaced with real ingestion, normalized event schemas, detection/correlation, alert storage and controlled playbooks.

Do not connect SOAR actions to production assets until policy and human approval gates are implemented.
