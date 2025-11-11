from sentence_transformers import SentenceTransformer
import os
import numpy as np
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Retriever:
    """Retrieves relevant chunks using cosine similarity."""

    def __init__(self, chunks: List[Dict], embeddings: List[np.ndarray], model_name: str = "all-mpnet-base-v2"):
        """
        Initialize retriever with chunks and their embeddings.

        Args:
            chunks: List of chunk dictionaries
            embeddings: List of numpy arrays (embeddings) corresponding to chunks
            model_name: Name of the sentence-transformers model to use for queries
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have same length")

        self.chunks = chunks
        self.embeddings = np.array(embeddings)  # Convert to numpy array for efficient operations
        self.model_name = model_name
        self._model = None
        self._query_embedding_cache = {}  # Cache for query embeddings

    def _get_model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.

        Args:
            query: The query string

        Returns:
            Numpy array representing the query embedding
        """
        # Check cache first
        if query in self._query_embedding_cache:
            return self._query_embedding_cache[query]

        try:
            model = self._get_model()
            embedding = model.encode(query, convert_to_numpy=True)
            self._query_embedding_cache[query] = embedding
            return embedding
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            # Return zero vector as fallback (will result in poor retrieval)
            # Use embedding dimension from the first chunk embedding
            emb_dim = len(self.embeddings[0]) if len(self.embeddings) > 0 else 384
            return np.zeros(emb_dim)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _find_top_k(self, query_embedding: np.ndarray, top_k: int) -> List[tuple[int, float]]:
        """
        Find top-k most similar chunks using cosine similarity.
        
        Args:
            query_embedding: Embedding vector for the query
            top_k: Number of top results to return
            
        Returns:
            List of tuples (chunk_index, similarity_score) sorted by similarity (descending)
        """
        # Calculate cosine similarities for all chunks
        # Use vectorized operations for efficiency
        dot_products = np.dot(self.embeddings, query_embedding)
        norms_query = np.linalg.norm(query_embedding)
        norms_chunks = np.linalg.norm(self.embeddings, axis=1)
        
        # Avoid division by zero
        denominators = norms_query * norms_chunks
        similarities = np.where(denominators > 0, dot_products / denominators, 0.0)
        
        # Get top-k indices
        top_k_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return list of (index, similarity) tuples
        results = [(int(idx), float(similarities[idx])) for idx in top_k_indices]
        return results
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: The query string (question)
            top_k: Number of chunks to retrieve
            
        Returns:
            List of chunk dictionaries with added 'similarity' field, sorted by relevance
        """
        if not query or not query.strip():
            print("Warning: Empty query. Returning empty results.")
            return []
        
        if top_k <= 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._get_query_embedding(query)
            
            # Find top-k chunks
            top_k_results = self._find_top_k(query_embedding, min(top_k, len(self.chunks)))
            
            # Build result list with similarity scores
            results = []
            for chunk_idx, similarity in top_k_results:
                chunk = self.chunks[chunk_idx].copy()
                chunk["similarity"] = similarity
                results.append(chunk)
            
            return results
            
        except Exception as e:
            print(f"Error during retrieval: {e}. Returning empty results.")
            return []

