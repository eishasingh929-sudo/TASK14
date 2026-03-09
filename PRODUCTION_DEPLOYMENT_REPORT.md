# PRODUCTION_DEPLOYMENT_REPORT

## Deployment Overview
UniGuru has been transitioned from a local development service to a secured, containerized production system within the BHIV ecosystem.

## Infrastructure Stack
- **OS**: Linux (Containerized)
- **Runtime**: Python 3.12 (uvicorn)
- **Scale**: 4 Workers
- **Edge Gateway**: NGINX 1.27
- **TLS**: Certbot (Let's Encrypt)
- **Domain**: `uni-guru.in`

## Security Hardening
- **API Authentication**: Enforced Bearer Token auth for `/ask`, `/metrics`, and dashboard.
- **Caller Governance**: Validation of `context.caller` or `X-Caller-Name` against allowed set (`bhiv-assistant`, `gurukul-platform`, `internal-testing`).
- **Network Isolation**: Only ports 80 and 443 exposed via NGINX; UniGuru service isolated in internal bridge network.
- **TLS 1.2+**: Modern cipher suites and HSTS enabled.

## Observability
- **Prometheus Metrics**: Available at `/metrics` (authenticated).
- **Live Dashboard**: Available at `/monitoring/dashboard` (authenticated).
- **Logging**: JSON-structured access logs in NGINX and application request logging.

## Verification Proof
- **Health Endpoint**: `https://uni-guru.in/health` -> `200 OK`
- **Ready Endpoint**: `https://uni-guru.in/ready` -> `200 OK`
- **Metrics Endpoint**: `https://uni-guru.in/metrics` -> `200 OK` (with token)
- **Ask Endpoint**: `https://uni-guru.in/ask` -> `200 OK` (with token and caller)
