from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
import re

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ChatRequest(BaseModel):
    messages: list

@app.post("/api/guardrails")
async def guardrails(request: Request):
    data = await request.json()
    chat_request = ChatRequest(**data)
    
    # Validate input
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
        
    # Check for prohibited words
    prohibited = ["malicious", "harm", "attack", "inappropriate"]
    for message in chat_request.messages:
        if any(word in message.content.lower() for word in prohibited):
            raise HTTPException(status_code=400, detail="Prohibited content detected")
            
    try:
        # Process request through LLM server
        response = requests.post(
            "http://llm-server:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": chat_request.messages[-1].content,
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        
        # Get the response from LLM server
        llm_response = response.json()
        
        # Validate and filter the response
        filtered_response = filter_content(llm_response["response"])
        
        return {
            "model": "llama3.2:1b",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": filtered_response
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def filter_content(text):
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-f-A-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\+?\d{10,}', '', text)
    
    return text