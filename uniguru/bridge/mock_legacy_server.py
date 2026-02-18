from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class LegacyRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(request: LegacyRequest):
    return {
        "answer": f"Legacy Generative response for: {request.message}",
        "source": "VectorDB_v1",
        "confidence": 0.95
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
