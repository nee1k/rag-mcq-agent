from sentence_transformers import SentenceTransformer
import os
import json
import hashlib
import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TextbookProcessor:
    """Processes textbook into chunks and generates embeddings."""
    
    def __init__(self, textbook_path: str, cache_dir: str = ".cache", model_name: str = "all-mpnet-base-v2"):
        self.textbook_path = textbook_path
        self.cache_dir = cache_dir
        self.model_name = model_name
        self._cached_chunks = None
        self._cached_embeddings = None
        self._model = None

        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

    def _get_model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def load_textbook(self) -> str:
        """Load textbook from file."""
        try:
            with open(self.textbook_path, 'r', encoding='utf-8') as f:
                text = f.read()
            if not text or len(text.strip()) == 0:
                raise ValueError(f"Textbook file is empty: {self.textbook_path}")
            # Normalize whitespace but preserve structure
            text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
            return text.strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Textbook file not found: {self.textbook_path}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Error decoding textbook file: {e}")
    
    def chunk_textbook(self, text: str, chunk_size: int = 800, overlap: int = 50) -> List[Dict]:
        """
        Chunk text into semantic chunks.
        
        Args:
            text: The text to chunk
            chunk_size: Target chunk size in tokens (~4 chars per token)
            overlap: Overlap size in tokens between chunks
            
        Returns:
            List of chunk dictionaries with text, start_char, end_char, chunk_index
        """
        # Convert token sizes to character sizes (approximate: 4 chars = 1 token)
        chunk_size_chars = chunk_size * 4
        overlap_chars = overlap * 4
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If paragraph fits in current chunk, add it
            if len(current_chunk) + len(para) + 2 <= chunk_size_chars:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Finalize current chunk if it exists
                if current_chunk:
                    chunks.append({
                        "text": current_chunk,
                        "start_char": current_start,
                        "end_char": current_start + len(current_chunk),
                        "chunk_index": chunk_index
                    })
                    chunk_index += 1
                    
                    # Start new chunk with overlap
                    overlap_start = max(0, len(current_chunk) - overlap_chars)
                    overlap_text = current_chunk[overlap_start:]
                    current_start = current_start + overlap_start
                    current_chunk = overlap_text + "\n\n" + para if overlap_text else para
                else:
                    # Paragraph is too large, split by sentences
                    sentences = re.split(r'([.!?]\s+)', para)
                    sentence_pairs = []
                    for i in range(0, len(sentences) - 1, 2):
                        if i + 1 < len(sentences):
                            sentence_pairs.append(sentences[i] + sentences[i + 1])
                        else:
                            sentence_pairs.append(sentences[i])
                    
                    for sent in sentence_pairs:
                        sent = sent.strip()
                        if not sent:
                            continue
                        
                        if len(current_chunk) + len(sent) + 1 <= chunk_size_chars:
                            current_chunk += " " + sent if current_chunk else sent
                        else:
                            if current_chunk:
                                chunks.append({
                                    "text": current_chunk,
                                    "start_char": current_start,
                                    "end_char": current_start + len(current_chunk),
                                    "chunk_index": chunk_index
                                })
                                chunk_index += 1
                                
                                # Overlap
                                overlap_start = max(0, len(current_chunk) - overlap_chars)
                                overlap_text = current_chunk[overlap_start:]
                                current_start = current_start + overlap_start
                                current_chunk = overlap_text + " " + sent if overlap_text else sent
                            else:
                                # Sentence too long, split by words
                                words = sent.split()
                                for word in words:
                                    if len(current_chunk) + len(word) + 1 <= chunk_size_chars:
                                        current_chunk += " " + word if current_chunk else word
                                    else:
                                        if current_chunk:
                                            chunks.append({
                                                "text": current_chunk,
                                                "start_char": current_start,
                                                "end_char": current_start + len(current_chunk),
                                                "chunk_index": chunk_index
                                            })
                                            chunk_index += 1
                                            overlap_start = max(0, len(current_chunk) - overlap_chars)
                                            overlap_text = current_chunk[overlap_start:]
                                            current_start = current_start + overlap_start
                                            current_chunk = overlap_text + " " + word if overlap_text else word
                                        else:
                                            current_chunk = word
                
                # Check if we need to finalize after adding paragraph
                if len(current_chunk) >= chunk_size_chars:
                    chunks.append({
                        "text": current_chunk,
                        "start_char": current_start,
                        "end_char": current_start + len(current_chunk),
                        "chunk_index": chunk_index
                    })
                    chunk_index += 1
                    overlap_start = max(0, len(current_chunk) - overlap_chars)
                    overlap_text = current_chunk[overlap_start:]
                    current_start = current_start + overlap_start
                    current_chunk = overlap_text
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk,
                "start_char": current_start,
                "end_char": current_start + len(current_chunk),
                "chunk_index": chunk_index
            })
        
        return chunks
    
    def _calculate_textbook_hash(self, text: str) -> str:
        """Calculate SHA256 hash of textbook content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def generate_embeddings(self, chunks: List[Dict], force_regenerate: bool = False) -> List[np.ndarray]:
        """
        Generate embeddings for chunks using sentence-transformers (local model).

        Args:
            chunks: List of chunk dictionaries
            force_regenerate: If True, regenerate even if cache exists

        Returns:
            List of numpy arrays (embeddings)
        """
        model = self._get_model()
        batch_size = 32  # sentence-transformers works well with smaller batches
        all_embeddings = []

        print(f"Generating embeddings for {len(chunks)} chunks...")

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_texts = [chunk["text"] for chunk in batch]

            try:
                # Generate embeddings using sentence-transformers
                batch_embeddings = model.encode(batch_texts, show_progress_bar=False, convert_to_numpy=True)
                all_embeddings.extend(batch_embeddings)

                # Progress logging
                if (i + batch_size) % 500 == 0 or i + batch_size >= len(chunks):
                    print(f"Processed {min(i + batch_size, len(chunks))}/{len(chunks)} chunks ({(min(i + batch_size, len(chunks)) / len(chunks) * 100):.1f}%)")

            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
                raise

        return [np.array(emb) for emb in all_embeddings]
    
    def save_embeddings_cache(self, chunks: List[Dict], embeddings: List[np.ndarray], textbook_hash: str):
        """Save chunks and embeddings to cache file."""
        cache_path = os.path.join(self.cache_dir, "textbook_embeddings.json")
        
        # Convert numpy arrays to lists for JSON serialization
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        cache_data = {
            "chunks": chunks,
            "embeddings": embeddings_list,
            "metadata": {
                "textbook_hash": textbook_hash,
                "model": self.model_name,
                "chunk_size": 800,
                "overlap": 50,
                "num_chunks": len(chunks),
                "created_at": str(np.datetime64('now'))
            }
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print(f"Cache saved to {cache_path}")
        except Exception as e:
            print(f"Error saving cache: {e}")
            raise
    
    def load_embeddings_cache(self) -> Optional[Tuple[List[Dict], List[np.ndarray], str]]:
        """Load chunks and embeddings from cache file."""
        cache_path = os.path.join(self.cache_dir, "textbook_embeddings.json")
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Validate cache structure
            if "chunks" not in cache_data or "embeddings" not in cache_data or "metadata" not in cache_data:
                print("Warning: Invalid cache structure. Regenerating embeddings.")
                return None
            
            chunks = cache_data["chunks"]
            embeddings_list = cache_data["embeddings"]
            embeddings = [np.array(emb) for emb in embeddings_list]
            textbook_hash = cache_data["metadata"].get("textbook_hash", "")
            cached_model = cache_data["metadata"].get("model", "")

            # Check if cache was created with the same model
            if cached_model != self.model_name:
                print(f"Warning: Cache was created with model '{cached_model}', but using '{self.model_name}'. Regenerating.")
                return None

            # Validate embeddings exist and have consistent dimensions
            if embeddings and len(embeddings) > 0:
                emb_dim = len(embeddings[0])
                if emb_dim == 0:
                    print(f"Warning: Invalid embedding dimension {emb_dim}. Regenerating.")
                    return None

            print(f"Loaded {len(chunks)} chunks from cache (model: {cached_model})")
            return chunks, embeddings, textbook_hash
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading cache: {e}. Regenerating embeddings.")
            return None
    
    def process(self, force_regenerate: bool = False) -> Tuple[List[Dict], List[np.ndarray]]:
        """
        Main processing method: load textbook, chunk, generate/load embeddings.
        
        Args:
            force_regenerate: If True, regenerate embeddings even if cache exists
            
        Returns:
            Tuple of (chunks, embeddings)
        """
        # Check cache first
        if not force_regenerate:
            cached = self.load_embeddings_cache()
            if cached:
                chunks, embeddings, cached_hash = cached
                # Verify textbook hasn't changed
                try:
                    text = self.load_textbook()
                    current_hash = self._calculate_textbook_hash(text)
                    if current_hash == cached_hash:
                        self._cached_chunks = chunks
                        self._cached_embeddings = embeddings
                        return chunks, embeddings
                    else:
                        print("Textbook file changed. Regenerating embeddings.")
                except Exception as e:
                    print(f"Error verifying textbook: {e}. Regenerating embeddings.")
        
        # Process textbook
        print("Processing textbook...")
        text = self.load_textbook()
        textbook_hash = self._calculate_textbook_hash(text)
        
        print("Chunking textbook...")
        chunks = self.chunk_textbook(text)
        print(f"Created {len(chunks)} chunks")
        
        print("Generating embeddings...")
        embeddings = self.generate_embeddings(chunks)
        
        # Save cache
        try:
            self.save_embeddings_cache(chunks, embeddings, textbook_hash)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
        
        self._cached_chunks = chunks
        self._cached_embeddings = embeddings
        
        return chunks, embeddings


