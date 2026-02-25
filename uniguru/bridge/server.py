import time
import uuid
import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uniguru.core.engine import RuleEngine

app = FastAPI()
engine = RuleEngine()

LEGACY_URL = os.getenv("UNIGURU_BACKEND_URL", "http://localhost:8000/api/v1/chat/new")
LEGACY_TIMEOUT = 5
MAX_SEVERITY_FORWARD = 0.5  # Anything >= blocks forwarding


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str
    source: str


@app.get("/")
async def health_check():
    return {"status": "UniGuru Bridge Running"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "uniguru-bridge"}


@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.perf_counter()
    trace_id = str(uuid.uuid4())

    # ---------- 1. Engine Evaluation (Fail-Closed Protected) ----------
    try:
        decision_result = engine.evaluate(
            content=request.message,
            metadata={
                "session_id": request.session_id,
                "source": request.source,
                "trace_id": trace_id
            }
        )
    except Exception as e:
        # SECTION 6 — FAIL-CLOSED GUARANTEE
        return {
            "trace_id": trace_id,
            "status": "blocked",
            "reason": f"System integrity failure: {str(e)}",
            "enforced": False,
            "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
        }

    # ---------- 2. Mandatory Enforcement Verification ----------
    # SECTION 5: Require enforced == True before returning answer or forward
    enforced = decision_result.get("enforced", False)
    decision_type = decision_result.get("decision")
    severity = decision_result.get("severity", 0.0)
    governance_flags = decision_result.get("governance_flags", {})
    data = decision_result.get("data", {})

    if not enforced:
        return {
            "trace_id": trace_id,
            "status": "blocked",
            "reason": decision_result.get("reason", "Enforcement validation missing"),
            "enforced": False,
            "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
        }

    # ---------- 3. Strict Decision Validation ----------
    if decision_type not in {"block", "answer", "forward"}:
        return {
            "trace_id": trace_id,
            "status": "blocked",
            "reason": "Invalid decision state",
            "enforced": False,
            "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
        }

    # ---------- 4. BLOCK Path ----------
    if decision_type == "block":
        return {
            "trace_id": trace_id,
            "status": "blocked",
            "reason": decision_result.get("reason", "Policy violation"),
            "severity": severity,
            "governance_flags": governance_flags,
            "enforced": True,
            "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
        }

    # ---------- 5. ANSWER Path ----------
    if decision_type == "answer":
        return {
            "trace_id": trace_id,
            "status": "answered",
            "data": data,
            "severity": severity,
            "governance_flags": governance_flags,
            "enforced": True,
            "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
        }

    # ---------- 6. FORWARD Path (Strictly Guarded) ----------
    if decision_type == "forward":
        # SECTION 5: Block forwarding if severity >= 0.5 or governance_flags not empty
        if severity >= MAX_SEVERITY_FORWARD or any(governance_flags.values()):
            return {
                "trace_id": trace_id,
                "status": "blocked",
                "reason": "Governance audit prevents forwarding high-risk query",
                "enforced": True,
                "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
            }

        try:
            legacy_payload = {
                "message": request.message,
                "session_id": request.session_id
            }

            response = requests.post(
                LEGACY_URL,
                json=legacy_payload,
                timeout=LEGACY_TIMEOUT
            )
            response.raise_for_status()

            return {
                "trace_id": trace_id,
                "status": "forwarded",
                "legacy_response": response.json(),
                "enforced": True,
                "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
            }

        except requests.exceptions.RequestException:
            # SECTION 6 — FAIL-CLOSED: Block when legacy server unavailable
            return {
                "trace_id": trace_id,
                "status": "blocked",
                "reason": "Legacy system unavailable - fail closed",
                "enforced": True, # The decision to block is enforced
                "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
            }

    # ---------- 7. Absolute Fallback (Should Never Happen) ----------
    return {
        "trace_id": trace_id,
        "status": "blocked",
        "reason": "Unhandled deterministic state",
        "enforced": False,
        "latency_ms": round(float((time.perf_counter() - start_time) * 1000), 2)
    }
