from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from collections import defaultdict, deque
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from uniguru.ontology.registry import OntologyRegistry
from uniguru.service.live_service import LiveUniGuruService
from uniguru.service.query_classifier import QueryType, classify_query


_LOG_LEVEL = os.getenv("UNIGURU_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, _LOG_LEVEL, logging.INFO))
logger = logging.getLogger("uniguru.service.api")


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = None
    allow_web: bool = False
    session_id: Optional[str] = Field(default=None, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "query" not in payload and "user_query" in payload:
            payload["query"] = payload.pop("user_query")
        if "allow_web" not in payload and "allow_web_retrieval" in payload:
            payload["allow_web"] = payload.pop("allow_web_retrieval")
        return payload

    @field_validator("query")
    @classmethod
    def _normalize_query(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("query must not be empty.")
        return normalized

    @field_validator("context")
    @classmethod
    def _validate_context(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if len(value) > 64:
            raise ValueError("context cannot contain more than 64 keys.")
        for key in value.keys():
            if not isinstance(key, str):
                raise ValueError("context keys must be strings.")
            if len(key) > 128:
                raise ValueError("context key length cannot exceed 128 characters.")
        encoded_len = len(json.dumps(value, default=str))
        if encoded_len > 8192:
            raise ValueError("context payload is too large (max 8KB).")
        return value


app = FastAPI(title="UniGuru Live Reasoning Service", version="1.1.0")
service = LiveUniGuruService()
registry = OntologyRegistry()
_START_TIME = time.time()
_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("UNIGURU_RATE_LIMIT_WINDOW_SECONDS", "60"))
_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("UNIGURU_RATE_LIMIT_MAX_REQUESTS", "60"))
_RATE_LIMIT_BUCKET: Dict[str, deque[float]] = defaultdict(deque)
_BUCKET_LOCK = threading.Lock()
_METRICS_LOCK = threading.Lock()
_ASK_REQUEST_TIMESTAMPS: deque[float] = deque()
_METRICS = {
    "requests_total": 0,
    "requests_by_status": defaultdict(int),
    "requests_ask_total": 0,
    "rate_limited_total": 0,
    "request_latency_ms_total": 0.0,
    "ask_verification_total": defaultdict(int),
    "ask_decision_total": defaultdict(int),
}


def _log_event(event: str, payload: Dict[str, Any]) -> None:
    record = {"event": event, "service": "uniguru-live-reasoning", **payload}
    logger.info(json.dumps(record, default=str, sort_keys=True))


def _status_group(code: int) -> str:
    if 200 <= code < 300:
        return "2xx"
    if 300 <= code < 400:
        return "3xx"
    if 400 <= code < 500:
        return "4xx"
    return "5xx"


def _is_rate_limited(client_id: str) -> bool:
    now = time.time()
    window_floor = now - _RATE_LIMIT_WINDOW_SECONDS
    with _BUCKET_LOCK:
        bucket = _RATE_LIMIT_BUCKET[client_id]
        while bucket and bucket[0] < window_floor:
            bucket.popleft()
        if len(bucket) >= _RATE_LIMIT_MAX_REQUESTS:
            return True
        bucket.append(now)
    return False


def _record_ask_metrics(decision: str, verification_status: str, latency_ms: float) -> None:
    now = time.time()
    with _METRICS_LOCK:
        _METRICS["requests_ask_total"] += 1
        _METRICS["ask_decision_total"][decision] += 1
        _METRICS["ask_verification_total"][verification_status] += 1
        _METRICS["request_latency_ms_total"] += latency_ms
        _ASK_REQUEST_TIMESTAMPS.append(now)
        floor = now - 60.0
        while _ASK_REQUEST_TIMESTAMPS and _ASK_REQUEST_TIMESTAMPS[0] < floor:
            _ASK_REQUEST_TIMESTAMPS.popleft()


def _validate_governance_input(query: str) -> None:
    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="query exceeds maximum length.")
    for char in query:
        codepoint = ord(char)
        if codepoint < 32 and char not in {"\n", "\r", "\t"}:
            raise HTTPException(status_code=400, detail="query contains unsupported control characters.")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    _log_event(
        event="invalid_request_rejected",
        payload={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.middleware("http")
async def observability_and_throttle(request: Request, call_next):
    started = time.perf_counter()
    if request.url.path.rstrip("/") == "/ask":
        client_id = request.client.host if request.client else "unknown"
        if _is_rate_limited(client_id):
            with _METRICS_LOCK:
                _METRICS["rate_limited_total"] += 1
                _METRICS["requests_total"] += 1
                _METRICS["requests_by_status"]["429"] += 1
            _log_event(
                event="rate_limit_enforced",
                payload={
                    "request_id": str(uuid.uuid4()),
                    "client_ip": client_id,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={
                    "X-RateLimit-Limit": str(_RATE_LIMIT_MAX_REQUESTS),
                    "X-RateLimit-Window-Seconds": str(_RATE_LIMIT_WINDOW_SECONDS),
                },
            )

    response = await call_next(request)
    latency_ms = (time.perf_counter() - started) * 1000
    with _METRICS_LOCK:
        _METRICS["requests_total"] += 1
        _METRICS["requests_by_status"][str(response.status_code)] += 1

    response.headers["X-RateLimit-Limit"] = str(_RATE_LIMIT_MAX_REQUESTS)
    response.headers["X-RateLimit-Window-Seconds"] = str(_RATE_LIMIT_WINDOW_SECONDS)
    response.headers["X-Request-Latency-Ms"] = f"{latency_ms:.2f}"
    return response


@app.post("/ask")
def ask(request: AskRequest) -> Dict[str, Any]:
    started = time.perf_counter()
    query = request.query
    _validate_governance_input(query)

    query_type = classify_query(query)
    effective_allow_web = bool(request.allow_web or query_type == QueryType.WEB_LOOKUP)

    context = dict(request.context or {})
    context["query_type"] = query_type.value

    response = service.ask(
        user_query=query,
        session_id=request.session_id,
        context=context,
        allow_web_retrieval=effective_allow_web,
    )
    latency_ms = (time.perf_counter() - started) * 1000

    decision = str(response.get("decision") or "unknown")
    verification_status = str(response.get("verification_status") or "UNVERIFIED")
    _record_ask_metrics(decision=decision, verification_status=verification_status, latency_ms=latency_ms)
    _log_event(
        event="request_processed",
        payload={
            "request_id": response.get("request_id") or str(uuid.uuid4()),
            "query_type": query_type.value,
            "latency": round(latency_ms, 3),
            "verification_status": verification_status,
            "decision": decision,
        },
    )
    return response


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "uniguru-live-reasoning",
        "version": app.version,
        "uptime_seconds": round(time.time() - _START_TIME, 3),
        "checks": {"ontology_registry": "ok", "reasoning_service": "ok"},
    }


@app.get("/ready")
@app.get("/health/ready")
def ready() -> Dict[str, Any]:
    return {"status": "ready", "service": "uniguru-live-reasoning"}


@app.get("/health/live")
def health_live() -> Dict[str, Any]:
    return {"status": "alive"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    with _METRICS_LOCK:
        requests_total = int(_METRICS["requests_total"])
        ask_total = int(_METRICS["requests_ask_total"])
        rate_limited_total = int(_METRICS["rate_limited_total"])
        by_status = dict(_METRICS["requests_by_status"])
        by_verification = dict(_METRICS["ask_verification_total"])
        by_decision = dict(_METRICS["ask_decision_total"])
        latency_total = float(_METRICS["request_latency_ms_total"])
        rpm = len(_ASK_REQUEST_TIMESTAMPS)

    success_count = int(by_verification.get("VERIFIED", 0)) + int(by_verification.get("PARTIAL", 0))
    verification_success_rate = (success_count / ask_total) if ask_total else 0.0
    average_latency = (latency_total / ask_total) if ask_total else 0.0

    lines = [
        "# TYPE uniguru_requests_total counter",
        f"uniguru_requests_total {requests_total}",
        "# TYPE uniguru_ask_requests_total counter",
        f"uniguru_ask_requests_total {ask_total}",
        "# TYPE uniguru_rate_limited_total counter",
        f"uniguru_rate_limited_total {rate_limited_total}",
        "# TYPE uniguru_requests_per_minute gauge",
        f"uniguru_requests_per_minute {rpm}",
        "# TYPE uniguru_verification_success_rate gauge",
        f"uniguru_verification_success_rate {verification_success_rate:.6f}",
        "# TYPE uniguru_request_latency_ms_avg gauge",
        f"uniguru_request_latency_ms_avg {average_latency:.3f}",
        "# TYPE uniguru_requests_by_status_total counter",
    ]
    for code, count in sorted(by_status.items()):
        lines.append(
            f'uniguru_requests_by_status_total{{code="{code}",group="{_status_group(int(code))}"}} {count}'
        )
    lines.append("# TYPE uniguru_ask_verification_status_total counter")
    for status, count in sorted(by_verification.items()):
        lines.append(f'uniguru_ask_verification_status_total{{status="{status}"}} {count}')
    lines.append("# TYPE uniguru_ask_decision_total counter")
    for decision, count in sorted(by_decision.items()):
        lines.append(f'uniguru_ask_decision_total{{decision="{decision}"}} {count}')
    return PlainTextResponse("\n".join(lines) + "\n")


@app.get("/monitoring/dashboard")
def monitoring_dashboard() -> Dict[str, Any]:
    with _METRICS_LOCK:
        ask_total = int(_METRICS["requests_ask_total"])
        rate_limited_total = int(_METRICS["rate_limited_total"])
        by_status = dict(_METRICS["requests_by_status"])
        by_verification = dict(_METRICS["ask_verification_total"])
        by_decision = dict(_METRICS["ask_decision_total"])
        latency_total = float(_METRICS["request_latency_ms_total"])
        rpm = len(_ASK_REQUEST_TIMESTAMPS)

    success_count = int(by_verification.get("VERIFIED", 0)) + int(by_verification.get("PARTIAL", 0))
    verification_success_rate = (success_count / ask_total) if ask_total else 0.0
    average_latency = (latency_total / ask_total) if ask_total else 0.0

    return {
        "service": "uniguru-live-reasoning",
        "uptime_seconds": round(time.time() - _START_TIME, 3),
        "traffic": {
            "ask_requests_total": ask_total,
            "rate_limited_total": rate_limited_total,
            "requests_per_minute": rpm,
            "average_latency_ms": round(average_latency, 3),
            "verification_success_rate": round(verification_success_rate, 6),
        },
        "status_codes": by_status,
        "decisions": by_decision,
        "verification_status": by_verification,
    }


@app.get("/ontology/concept/{concept_id}")
def ontology_concept(concept_id: str) -> Dict[str, Any]:
    try:
        return registry.get_concept(concept_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
