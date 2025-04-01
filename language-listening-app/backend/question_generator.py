from transformers import pipeline
from gtts import gTTS
import os
import playsound
import json

class QuestionGenerator:
    def __init__(self):
        # Initialize the question generation pipeline
        self.qa_generator = pipeline(
            "text2text-generation",
            model="facebook/bart-large-cnn",
            device=-1  # Use CPU
        )

    def generate(self, topic: str, num_questions: int = 5) -> dict:
        """Generate questions using a free NLP model"""
        try:
            # Create a prompt for question generation
            prompt = f"""
            Generate {num_questions} educational questions about {topic}.
            Format: Question text
            """
            
            # Generate questions using the model
            questions = self.qa_generator(
                prompt,
                max_length=100,
                num_return_sequences=num_questions,
                do_sample=True
            )
            
            # Format the questions
            questions_json = {
                "questions": [
                    {
                        "text": q["generated_text"].strip(),
                        "difficulty": "medium",
                        "topic": topic
                    }
                    for q in questions
                ]
            }
            
            # Generate audio for each question
            for question in questions_json["questions"]:
                audio_path = self.generate_audio(question["text"])
                question["audio_url"] = f"audio/{os.path.basename(audio_path)}"
            
            return questions_json
            
        except Exception as e:
            raise Exception(f"Failed to generate questions: {str(e)}")

    def generate_audio(self, text: str) -> str:
        """Generate audio using gTTS"""
        try:
            # Create audio file
            tts = gTTS(text=text, lang='en')
            filename = f"question_{hash(text)}.mp3"
            audio_path = os.path.join("audio", filename)
            
            # Save the audio file
            tts.save(audio_path)
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Failed to generate audio: {str(e)}")