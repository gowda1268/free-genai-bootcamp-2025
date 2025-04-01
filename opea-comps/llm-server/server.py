from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ChatRequest(BaseModel):
    messages: list

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    chat_request = ChatRequest(**data)
    
    try:
        # Process request through guardrails service
        response = requests.post(
            "http://guardrails-service:8000/api/guardrails",
            json=data
        )
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": str(e)}
