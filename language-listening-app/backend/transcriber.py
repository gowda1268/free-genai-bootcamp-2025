from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import os

class YouTubeTranscriber:
    def __init__(self):
        self.formatter = TextFormatter()
        self.cache_dir = "transcript_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, video_id: str) -> str:
        return os.path.join(self.cache_dir, f"{video_id}.txt")

    def _load_from_cache(self, video_id: str) -> str:
        cache_path = self._get_cache_path(video_id)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def _save_to_cache(self, video_id: str, transcript: str):
        cache_path = self._get_cache_path(video_id)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(transcript)

    def get_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:youtu.be\/|embed\/|v=|\/)([0-9A-Za-z_-]{11})',
            r'([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError("Invalid YouTube URL")

    def get_transcript(self, url: str) -> str:
        """Get transcript from YouTube video"""
        try:
            video_id = self.get_video_id(url)
            
            # Check cache first
            cached_transcript = self._load_from_cache(video_id)
            if cached_transcript:
                return cached_transcript

            # Get transcript from YouTube
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Format the transcript to plain text
            text = self.formatter.format_transcript(transcript)
            
            # Clean the transcript
            cleaned_text = self._clean_transcript(text)
            
            # Save to cache
            self._save_to_cache(video_id, cleaned_text)
            
            return cleaned_text
            
        except Exception as e:
            raise Exception(f"Failed to get transcript: {str(e)}")

    def _clean_transcript(self, text: str) -> str:
        """Clean the transcript text"""
        # Remove timestamps
        text = re.sub(r'\d+:\d+:\d+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        return text