import os
import sys
import requests
import uvicorn
import time
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Ensure parent directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import RuleEngine

app = FastAPI(title="UniGuru Admission Bridge")
engine = RuleEngine()

# Configuration
LEGACY_BACKEND_URL = "http://127.0.0.1:8080/chat"

class AdmitRequest(BaseModel):
    request_content: str
    metadata: Optional[Dict[str, Any]] = None

@app.get("/health")
def health():
    return {"status": "ok", "engine": "RLM v1.0.0"}

@app.post("/admit")
async def admit(request_data: AdmitRequest):
    start_time = time.perf_counter()
    
    try:
        # 1. Execute Rule Engine
        engine_response = engine.evaluate(
            request_data.request_content, 
            metadata=request_data.metadata
        )
        
        decision = engine_response["decision"]
        
        # 2. Handle Handover (FORWARD logic)
        if decision == "forward":
            try:
                legacy_res = requests.post(
                    LEGACY_BACKEND_URL,
                    json={"message": request_data.request_content},
                    timeout=5.0
                )
                legacy_data = legacy_res.json()
                
                # Enrich engine response with legacy data
                engine_response["response_content"] = legacy_data.get("answer")
                engine_response["reason"] = "Processed by Legacy Generative AI."
                engine_response["metadata"]["legacy_status"] = "success"
                
            except requests.exceptions.RequestException as e:
                # Failure in legacy handover - Treat as error
                engine_response["decision"] = "error"
                engine_response["reason"] = f"Handover failed: {str(e)}"
                engine_response["response_content"] = "System handover error. Please try again later."
        
        # 3. Final metrics
        end_time = time.perf_counter()
        engine_response["total_bridge_latency_ms"] = round((end_time - start_time) * 1000, 3)
        
        # 4. Standardized Output
        return engine_response

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Admission Error")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
