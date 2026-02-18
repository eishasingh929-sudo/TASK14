import time
import uuid
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.engine import RuleEngine

app = FastAPI()
engine = RuleEngine()

LEGACY_URL = "http://127.0.0.1:8080/chat"

class ChatRequest(BaseModel):
    message: str
    session_id: str
    source: str

@app.get("/")
async def health_check():
    return {"status": "UniGuru Bridge Running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.perf_counter()
    trace_id = str(uuid.uuid4())
    
    # Call the Rule Engine
    decision_result = engine.evaluate(
        content=request.message,
        metadata={
            "session_id": request.session_id,
            "source": request.source,
            "trace_id": trace_id
        }
    )
    
    decision_type = decision_result.get("decision")
    
    # 1. BLOCK Path
    if decision_type == "block":
        return {
            "trace_id": trace_id,
            "status": "blocked",
            "reason": decision_result.get("reason")
        }
    
    # 2. ANSWER Path (Deterministic KB Retrieval)
    if decision_type == "answer":
        return {
            "trace_id": trace_id,
            "status": "answered",
            "data": decision_result
        }
    
    # 3. FORWARD Path (Legacy Generative System)
    if decision_type == "forward":
        try:
            legacy_payload = {
                "message": request.message,
                "session_id": request.session_id
            }
            
            response = requests.post(
                LEGACY_URL, 
                json=legacy_payload, 
                timeout=5
            )
            response.raise_for_status()
            
            return {
                "trace_id": trace_id,
                "status": "forwarded",
                "legacy_response": response.json()
            }
            
        except requests.exceptions.RequestException as e:
            # Server unavailable or error
            raise HTTPException(status_code=502, detail=f"Legacy server error: {str(e)}")

    # Fallback/Unexpected Decision
    return {
        "trace_id": trace_id,
        "status": "processed",
        "decision": decision_result,
        "latency_ms": round((time.perf_counter() - start_time) * 1000, 2)
    }
