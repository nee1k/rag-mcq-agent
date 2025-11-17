from sentence_transformers import SentenceTransformer
import os
import numpy as np
from typing import List, Dict, Optional
from threading import Lock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import faiss
    _HAS_FAISS = True
except ImportError:
    faiss = None  # type: ignore
    _HAS_FAISS = False


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
        # Ensure embeddings are float32 for FAISS compatibility
        self.embeddings = np.array(embeddings, dtype=np.float32)
        self.model_name = model_name
        self._model = None
        self._model_lock = Lock()  # Lock for model initialization
        self._encode_lock = Lock()  # Lock for encoding operations
        self._query_embedding_cache = {}  # Cache for query embeddings

        # Pre-normalize embeddings for cosine similarity
        self._normalized_embeddings = self._normalize_vectors(self.embeddings)

        # Build FAISS index if available
        self._use_faiss = _HAS_FAISS and len(self._normalized_embeddings) > 0
        self._faiss_index = self._build_faiss_index(self._normalized_embeddings) if self._use_faiss else None

    def _get_model(self) -> SentenceTransformer:
        """Lazy load the embedding model (thread-safe)."""
        if self._model is None:
            with self._model_lock:
                if self._model is None:  # Double-check pattern
                    self._model = SentenceTransformer(self.model_name)
                    # Pre-warm the model to avoid meta tensor issues
                    try:
                        self._model.encode("warmup", convert_to_numpy=True)
                    except Exception:
                        pass  # Ignore warmup errors
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
            # Lock encoding operations to prevent concurrent access
            with self._encode_lock:
                embedding = model.encode(query, convert_to_numpy=True)
            self._query_embedding_cache[query] = embedding
            return embedding
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            # Return zero vector as fallback (will result in poor retrieval)
            # Use embedding dimension from the first chunk embedding
            emb_dim = len(self.embeddings[0]) if len(self.embeddings) > 0 else 384
            return np.zeros(emb_dim)
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors to unit length (safe for zero vectors)."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize a single vector."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _build_faiss_index(self, normalized_embeddings: np.ndarray):
        """Build FAISS index for fast similarity search."""
        if not _HAS_FAISS:
            return None

        dim = normalized_embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(normalized_embeddings)
        return index
    
    def _find_top_k(self, query_embedding: np.ndarray, top_k: int) -> List[tuple[int, float]]:
        """
        Find top-k most similar chunks using cosine similarity.
        
        Args:
            query_embedding: Embedding vector for the query
            top_k: Number of top results to return
            
        Returns:
            List of tuples (chunk_index, similarity_score) sorted by similarity (descending)
        """
        if len(self._normalized_embeddings) == 0:
            return []

        normalized_query = self._normalize_vector(query_embedding)
        similarities = np.dot(self._normalized_embeddings, normalized_query)
        
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
            normalized_query = self._normalize_vector(query_embedding.astype(np.float32))

            # Choose FAISS or numpy for similarity search
            if self._use_faiss and self._faiss_index is not None:
                distances, indices = self._faiss_index.search(
                    np.array([normalized_query], dtype=np.float32),
                    min(top_k, len(self.chunks))
                )
                top_k_results = [
                    (int(idx), float(dist))
                    for idx, dist in zip(indices[0], distances[0])
                    if idx != -1
                ]
            else:
                top_k_results = self._find_top_k(normalized_query, min(top_k, len(self.chunks)))
            
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

