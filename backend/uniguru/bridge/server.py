from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from uniguru.router.conversation_router import ConversationRouter

app = FastAPI(title="UniGuru Compatibility Bridge")
router = ConversationRouter()


class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    query: Optional[str] = None
    session_id: Optional[str] = None
    caller: str = "uniguru-frontend"
    allow_web: bool = False
    context: Optional[Dict[str, Any]] = None
    source: str = "bridge_compat"


class GurukulQueryRequest(BaseModel):
    student_query: str
    student_id: Optional[str] = None
    class_id: Optional[str] = None
    session_id: Optional[str] = None


def _extract_query(request: ChatRequest) -> str:
    return str(request.message or request.question or request.query or "").strip()


def _wrap_router_response(response: Dict[str, Any], trace_id: str, latency_ms: float) -> Dict[str, Any]:
    return {
        "status": "answered" if response.get("decision") == "answer" else "blocked",
        "trace_id": trace_id,
        "latency_ms": round(latency_ms, 2),
        "decision": response.get("decision"),
        "verification_status": response.get("verification_status"),
        "status_action": response.get("status_action"),
        "governance_flags": response.get("governance_flags", {}),
        "governance_output": response.get("governance_output", {}),
        "ontology_reference": response.get("ontology_reference"),
        "reasoning_trace": response.get("reasoning_trace"),
        "data": {
            "response_content": response.get("answer"),
            "engine_response": response,
        },
    }


@app.post("/chat")
async def chat_bridge(request: ChatRequest) -> Dict[str, Any]:
    query = _extract_query(request)
    if not query:
        raise HTTPException(status_code=400, detail="No valid query provided.")

    trace_id = str(uuid.uuid4())
    started = time.perf_counter()
    response = router.route_query(
        query=query,
        context={
            **(request.context or {}),
            "caller": request.caller,
            "session_id": request.session_id,
            "allow_web": bool(request.allow_web),
            "bridge_source": request.source,
            "trace_id": trace_id,
        },
    )
    latency_ms = (time.perf_counter() - started) * 1000
    return _wrap_router_response(response=response, trace_id=trace_id, latency_ms=latency_ms)


@app.post("/integrations/gurukul/chat")
async def gurukul_chat(request: GurukulQueryRequest) -> Dict[str, Any]:
    if not request.student_query.strip():
        raise HTTPException(status_code=400, detail="student_query is required.")

    trace_id = str(uuid.uuid4())
    started = time.perf_counter()
    response = router.route_query(
        query=request.student_query,
        context={
            "caller": "gurukul-platform",
            "session_id": request.session_id,
            "student_id": request.student_id,
            "class_id": request.class_id,
            "trace_id": trace_id,
        },
    )
    latency_ms = (time.perf_counter() - started) * 1000
    wrapped = _wrap_router_response(response=response, trace_id=trace_id, latency_ms=latency_ms)
    wrapped.update(
        {
            "integration": "gurukul",
            "student_id": request.student_id,
            "class_id": request.class_id,
            "session_id": request.session_id,
        }
    )
    return wrapped


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "bridge_mode": "compatibility-only",
        "canonical_entrypoint": "/ask",
        "router_available": True,
    }
