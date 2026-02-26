import time
import uuid
import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uniguru.core.engine import RuleEngine
from uniguru.enforcement.enforcement import UniGuruEnforcement

app = FastAPI(
    title="UniGuru Bridge",
    description="Production Bridge — governs real UniGuru backend with enforcement sealing.",
    version="2.0.0"
)
engine = RuleEngine()
enforcer = UniGuruEnforcement()

# ---- Configuration -------------------------------------------------------
# Phase 1: Point to REAL UniGuru production backend
# Change UNIGURU_BACKEND_URL env-var to override (e.g., if backend runs on a
# different port or host).
LEGACY_URL = os.getenv(
    "UNIGURU_BACKEND_URL",
    "http://localhost:8000/api/v1/chat/new"   # Real production UniGuru endpoint
)
LEGACY_TIMEOUT = int(os.getenv("LEGACY_TIMEOUT", "10"))
MAX_SEVERITY_FORWARD = 0.5        # Anything >= this blocks forwarding


# ---- Request / Response Models -------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    session_id: str = Field(..., description="Unique session identifier")
    source: str = Field(..., description="Request source label")


# ---- Helper: blocked response builder -----------------------------------
def _blocked(trace_id: str, reason: str, latency_ms: float,
             enforced: bool = False, severity: float = 0.0) -> dict:
    return {
        "trace_id": trace_id,
        "status": "blocked",
        "reason": reason,
        "severity": severity,
        "enforced": enforced,
        "enforcement_signature": None,
        "signature_verified": False,
        "latency_ms": round(float(latency_ms), 2),
    }


# ---- Endpoints -----------------------------------------------------------
@app.get("/")
async def root():
    return {
        "status": "UniGuru Bridge Running",
        "version": "2.0.0",
        "legacy_url": LEGACY_URL
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "uniguru-bridge", "version": "2.0.0"}


@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.perf_counter()
    trace_id = str(uuid.uuid4())

    # ==================================================================
    # STEP 1 — Rule Engine Evaluation (Fail-Closed Protected)
    # ==================================================================
    try:
        decision_result = engine.evaluate(
            content=request.message,
            metadata={
                "session_id": request.session_id,
                "source": request.source,
                "trace_id": trace_id,
            }
        )
    except Exception as e:
        return _blocked(trace_id, f"System integrity failure: {e}",
                        (time.perf_counter() - start_time) * 1000)

    # ==================================================================
    # STEP 2 — Enforcement Presence Check
    # Require enforced == True, AND verify cryptographic signature
    # ==================================================================
    enforced = decision_result.get("enforced", False)
    decision_type = decision_result.get("decision")
    severity = decision_result.get("severity", 0.0)
    governance_flags = decision_result.get("governance_flags", {})
    data = decision_result.get("data", {})
    enforcement_signature = decision_result.get("enforcement_signature")
    sealed_at = decision_result.get("sealed_at")

    latency_so_far = lambda: (time.perf_counter() - start_time) * 1000

    # 2a. Enforced flag check
    if not enforced:
        return _blocked(trace_id,
                        decision_result.get("reason", "Enforcement validation missing"),
                        latency_so_far())

    # 2b. Cryptographic Signature Verification (Phase 2 — Enforcement Sealing)
    # Bridge MUST verify signature before returning any response.
    # If signature is missing or invalid → BLOCK response.
    if decision_type in ("answer", "forward"):
        sig_valid = enforcer.verify_response(decision_result)
        if not sig_valid:
            return _blocked(trace_id,
                            "ENFORCEMENT SEAL VIOLATION: Response signature missing or invalid.",
                            latency_so_far(), enforced=False)

    # ==================================================================
    # STEP 3 — Decision Validation
    # ==================================================================
    if decision_type not in {"block", "answer", "forward"}:
        return _blocked(trace_id, "Invalid decision state", latency_so_far())

    # ==================================================================
    # STEP 4 — BLOCK Path
    # ==================================================================
    if decision_type == "block":
        return {
            "trace_id": trace_id,
            "status": "blocked",
            "reason": decision_result.get("reason", "Policy violation"),
            "severity": severity,
            "governance_flags": governance_flags,
            "enforced": True,
            "enforcement_signature": enforcement_signature,
            "signature_verified": decision_result.get("signature_verified", False),
            "sealed_at": sealed_at,
            "latency_ms": round(float(latency_so_far()), 2),
        }

    # ==================================================================
    # STEP 5 — ANSWER Path (served from UniGuru Knowledge Base)
    # ==================================================================
    if decision_type == "answer":
        return {
            "trace_id": trace_id,
            "status": "answered",
            "data": data,
            "severity": severity,
            "governance_flags": governance_flags,
            "enforced": True,
            "enforcement_signature": enforcement_signature,
            "signature_verified": decision_result.get("signature_verified", False),
            "sealed_at": sealed_at,
            "latency_ms": round(float(latency_so_far()), 2),
        }

    # ==================================================================
    # STEP 6 — FORWARD Path (sends to real UniGuru production backend)
    #          Phase 1: User → Bridge → UniGuru → Response → Bridge → User
    # ==================================================================
    if decision_type == "forward":
        # Block forwarding if governance flags or high severity
        if severity >= MAX_SEVERITY_FORWARD or any(governance_flags.values()):
            return {
                "trace_id": trace_id,
                "status": "blocked",
                "reason": "Governance audit prevents forwarding high-risk query",
                "enforced": True,
                "enforcement_signature": enforcement_signature,
                "signature_verified": decision_result.get("signature_verified", False),
                "latency_ms": round(float(latency_so_far()), 2),
            }

        try:
            legacy_payload = {
                "message": request.message,
                "session_id": request.session_id,
            }

            legacy_resp = requests.post(
                LEGACY_URL,
                json=legacy_payload,
                timeout=LEGACY_TIMEOUT
            )
            legacy_resp.raise_for_status()

            # Re-sign the forwarded response with Bridge enforcement seal
            legacy_data = legacy_resp.json()
            forwarded_content = str(legacy_data)
            forward_sig = enforcer.generate_signature(forwarded_content, trace_id)
            forward_sig_valid = enforcer.verify_signature(forwarded_content, trace_id, forward_sig)

            return {
                "trace_id": trace_id,
                "status": "forwarded",
                "legacy_response": legacy_data,
                "enforced": True,
                "enforcement_signature": forward_sig,
                "signature_verified": forward_sig_valid,
                "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "forwarded_to": LEGACY_URL,
                "latency_ms": round(float(latency_so_far()), 2),
            }

        except requests.exceptions.ConnectionError:
            return _blocked(trace_id,
                            f"Legacy system unavailable at {LEGACY_URL} — fail closed",
                            latency_so_far(), enforced=True)
        except requests.exceptions.Timeout:
            return _blocked(trace_id,
                            f"Legacy system timed out after {LEGACY_TIMEOUT}s — fail closed",
                            latency_so_far(), enforced=True)
        except requests.exceptions.HTTPError as e:
            return _blocked(trace_id,
                            f"Legacy system HTTP error: {e} — fail closed",
                            latency_so_far(), enforced=True)
        except requests.exceptions.RequestException as e:
            return _blocked(trace_id,
                            f"Legacy system request failed: {e} — fail closed",
                            latency_so_far(), enforced=True)

    # ==================================================================
    # ABSOLUTE FALLBACK (Should never reach here)
    # ==================================================================
    return _blocked(trace_id, "Unhandled deterministic state", latency_so_far())
