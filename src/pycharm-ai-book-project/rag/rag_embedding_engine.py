from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingEngine:

    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def encode_documents(self, documents):
        """Batch encode documents for efficiency"""
        embeddings = self.model.encode(
            documents,
            batch_size=32,
            show_progress_bar=True
        )
        
        return embeddings
    
    def calculate_similarity(self, query_embedding, doc_embeddings):
        """Calculate cosine similarity between query and documents"""
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
         # Calculate cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        
        return similarities