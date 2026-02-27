import os
import time
import uuid
from typing import Dict, Any, Optional, List
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uniguru.core.engine import RuleEngine
from uniguru.enforcement.enforcement import SovereignEnforcement
from uniguru.bridge.auth import generate_bridge_token

app = FastAPI(title="UniGuru Sovereign Bridge")

# Production UniGuru Backend URL (Phase 1 target endpoint)
LEGACY_URL = os.getenv(
    "LEGACY_URL",
    os.getenv("UNIGURU_BACKEND_URL", "http://localhost:8000/api/v1/chat/new")
)
BRIDGE_USER_ID = os.getenv("BRIDGE_USER_ID")
BRIDGE_CHATBOT_ID = os.getenv("BRIDGE_CHATBOT_ID")

engine = RuleEngine()
enforcer = SovereignEnforcement()

class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    query: Optional[str] = None
    session_id: Optional[str] = None
    source: str = "bridge_v2"

@app.post("/chat")
async def chat_bridge(request: ChatRequest):
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    user_msg = request.message or request.question or request.query

    if not user_msg:
        raise HTTPException(status_code=400, detail="No valid query provided.")

    # 1. Pipeline Start: Rule Engine Logic
    # (Internally uses the Upgraded Multi-Source Retriever)
    decision = engine.evaluate(user_msg, {"session_id": request.session_id, "trace_id": trace_id})
    
    # 2. Handle Production Forwarding
    if decision.get("decision") == "forward":
        try:
            token = generate_bridge_token()
            # Forwarding Flow: Bridge -> Production UniGuru
            resp = requests.post(
                LEGACY_URL,
                json={
                    "message": user_msg,
                    "session_id": request.session_id,
                    "userId": BRIDGE_USER_ID,
                    "chatbotId": BRIDGE_CHATBOT_ID
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                timeout=10
            )
            resp.raise_for_status()
            production_data = resp.json()
            
            # Bridge -> Enforcement (Post-production verification)
            decision["legacy_response"] = production_data
            prod_answer = (
                production_data.get("answer")
                or (production_data.get("aiResponse") or {}).get("content")
                or "No answer from production."
            )
            decision["data"] = {"response_content": str(prod_answer)}
            decision["verification_status"] = "PARTIAL" # Forwarded responses are marked PARTIAL for safety
            
        except Exception as e:
            decision = {
                "decision": "block",
                "reason": f"Production Backend Unavailable: {str(e)}",
                "data": {"response_content": "The production ecosystem is currently unreachable. Safety override activated."}
            }

    # 3. Final Pipeline Stage: Enforce and Seal
    # This seals both Local KB and Forwarded responses.
    sealed_response = enforcer.process_and_seal(decision, trace_id)

    # 4. Mandatory Bridge Audit (Verify Seal)
    if not enforcer.verify_bridge_seal(sealed_response):
        raise HTTPException(status_code=500, detail="Enforcement Seal Violation: Tampering Detected.")

    latency = (time.time() - start_time) * 1000
    sealed_response["latency_ms"] = round(latency, 2)
    sealed_response["trace_id"] = trace_id

    return sealed_response

@app.get("/health")
def health():
    return {"status": "ok", "bridge_version": "2.1.0", "production_target": LEGACY_URL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
