from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class DocumentRetriever:
    def __init__(self, document_db):
        self.document_db = document_db
        self.sections = self.document_db.get_all_sections()
        self.vectorizer = TfidfVectorizer()
        if self.sections:
            contents = [content for _, content in self.sections]
            self.tfidf_matrix = self.vectorizer.fit_transform(contents)
        else:
            self.tfidf_matrix = None
    
    def get_relevant_sections(self, query, top_k=3):
        """Retrieve top relevant sections using cosine similarity"""
        if not self.sections or self.tfidf_matrix is None:
            return []
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                relevant.append(self.sections[idx])
        
        return relevant