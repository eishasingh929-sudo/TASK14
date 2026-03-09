# UniGuru Deployment Readiness Checklist

This checklist tracks the transition of UniGuru into a live production system within the BHIV ecosystem.

## 1. System Audit
- [x] Review `service/api.py`
- [x] Review `live_service.py`
- [x] Review `API_SPEC.md`
- [x] Confirm endpoints: `/ask`, `/health`, `/ready`, `/metrics`, `/monitoring/dashboard`

## 2. API Authentication (Day 1)
- [x] Implement/Harden API token authentication in `service/api.py`.
- [x] Ensure `Authorization: Bearer` is supported.
- [x] Ensure 401 Unauthorized is returned for missing/invalid tokens.
- [x] Use `UNIGURU_API_TOKEN` environment variable.
- [x] Ensure no hardcoded credentials.

## 3. Service Access Control (Day 2)
- [ ] Add explicit caller identification validation.
- [ ] Allow `bhiv-assistant`, `gurukul-platform`, `internal-testing`.
- [ ] Reject unknown callers with 403 Forbidden.

## 4. Reverse Proxy Setup (Day 2)
- [ ] Prepare NGINX configuration for `uni-guru.in`.
- [ ] Implement rate limit protection.
- [ ] Configure request logging and header forwarding.

## 5. Production Deployment Configuration (Day 3)
- [ ] Create `docker-compose.yml` for production.
- [ ] Prepare startup script with `uvicorn`.
- [ ] Configure worker scaling.

## 6. Domain, TLS & Integration (Day 4)
- [ ] Configure `uni-guru.in` domain.
- [ ] Setup HTTPS/TLS certificates (Let's Enrypt).
- [ ] Integrate UniGuru with BHIV Assistant.

## 7. Validation & Launch (Day 5)
- [ ] Run cross-system integration tests.
- [ ] Produce `PRODUCTION_DEPLOYMENT_REPORT.md`.
- [ ] Produce `PUBLIC_API_USAGE.md`.
- [ ] Produce `LAUNCH_VALIDATION.md`.
