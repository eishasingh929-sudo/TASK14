# UniGuru Production Runbook

## 1. Pre-deploy
- Copy `.env.production.example` to `.env.production`.
- Set a strong `UNIGURU_API_TOKEN`.
- Confirm `UNIGURU_ALLOWED_CALLERS` includes only approved BHIV systems.

## 2. Start Stack
```bash
docker compose up -d --build
```

## 3. Bootstrap TLS Certificate
```bash
sh deploy/certbot/bootstrap.sh uni-guru.in ops@uni-guru.in
```

## 4. Smoke Checks
```bash
curl -sS https://uni-guru.in/health
curl -sS -H "Authorization: Bearer <token>" https://uni-guru.in/metrics
curl -sS -X POST https://uni-guru.in/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Caller-Name: bhiv-assistant" \
  -d '{"query":"What is a qubit?","context":{"caller":"bhiv-assistant"}}'
```

## 5. Zero-downtime Restart
```bash
docker compose pull
docker compose up -d --build
```

## 6. Rollback
```bash
docker compose down
git checkout <last-known-good-tag>
docker compose up -d --build
```

## 7. Ongoing Operations
- Certbot auto-renew runs in the `certbot` service every 12 hours.
- If certificates are renewed manually:
```bash
sh deploy/certbot/renew.sh
```
