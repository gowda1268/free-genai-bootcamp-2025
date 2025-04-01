from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import json

class VectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.documents = []
        self.vectors = None
        self.metadata = []
        self.persist_file = "vector_store.json"

        # Load existing data if available
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.persist_file):
            with open(self.persist_file, 'r') as f:
                data = json.load(f)
                self.documents = data.get('documents', [])
                self.metadata = data.get('metadata', [])

    def _save_data(self):
        with open(self.persist_file, 'w') as f:
            json.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)

    def add_text(self, text: str, metadata: dict = None):
        """Add text to the vector store"""
        try:
            # Add new document
            self.documents.append(text)
            if metadata:
                self.metadata.append(metadata)
            else:
                self.metadata.append({})

            # Update vectors
            self.vectors = self.vectorizer.fit_transform(self.documents)
            
            # Save changes
            self._save_data()
            
        except Exception as e:
            raise Exception(f"Failed to add text to vector store: {str(e)}")

    def get_similar_questions(self, query: str, n_results: int = 5):
        """Get similar questions based on the query"""
        try:
            if not self.documents:
                return []

            # Transform query
            query_vec = self.vectorizer.transform([query])

            # Calculate similarities
            similarities = cosine_similarity(query_vec, self.vectors).flatten()
            
            # Get top n results
            top_indices = np.argsort(similarities)[-n_results:][::-1]
            
            # Return similar questions
            return [self.documents[i] for i in top_indices]
            
        except Exception as e:
            raise Exception(f"Failed to get similar questions: {str(e)}")

    def clear_store(self):
        """Clear the vector store"""
        try:
            self.documents = []
            self.vectors = None
            self.metadata = []
            self._save_data()
        except Exception as e:
            raise Exception(f"Failed to clear vector store: {str(e)}")