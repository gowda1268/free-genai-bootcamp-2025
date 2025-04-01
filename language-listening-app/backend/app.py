from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transcriber import YouTubeTranscriber
from vector_store import VectorStore
from question_generator import QuestionGenerator
import os

app = FastAPI()

class YouTubeURL(BaseModel):
    url: str

class Topic(BaseModel):
    topic: str

# Initialize components
transcriber = YouTubeTranscriber()
vector_store = VectorStore()
question_generator = QuestionGenerator()

@app.post("/transcribe")
async def transcribe_video(youtube_url: YouTubeURL):
    try:
        transcript = transcriber.get_transcript(youtube_url.url)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-questions")
async def generate_questions(topic: Topic):
    try:
        questions = question_generator.generate(topic.topic)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar-questions")
async def get_similar_questions(topic: str):
    try:
        similar_questions = vector_store.get_similar_questions(topic)
        return {"similar_questions": similar_questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)