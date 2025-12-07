"""
Embeddings Utility
Handle text embeddings for semantic similarity
"""
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """Manage text embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embeddings manager
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.model = None
    
    def encode(self, texts: List[str], batch_size: int = 32) -> Optional[np.ndarray]:
        """
        Encode texts to embeddings
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings or None if model not loaded
        """
        if self.model is None:
            logger.warning("Embedding model not loaded")
            return None
        
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
            return embeddings
        
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            return None
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if self.model is None:
            return 0.0
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            emb1 = self.encode([text1])
            emb2 = self.encode([text2])
            
            if emb1 is None or emb2 is None:
                return 0.0
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def batch_similarity(self, query: str, candidates: List[str]) -> List[float]:
        """
        Calculate similarity between query and multiple candidates
        
        Args:
            query: Query text
            candidates: List of candidate texts
            
        Returns:
            List of similarity scores
        """
        if self.model is None:
            return [0.0] * len(candidates)
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            query_emb = self.encode([query])
            candidate_embs = self.encode(candidates)
            
            if query_emb is None or candidate_embs is None:
                return [0.0] * len(candidates)
            
            similarities = cosine_similarity(query_emb, candidate_embs)[0]
            return similarities.tolist()
        
        except Exception as e:
            logger.error(f"Error calculating batch similarity: {e}")
            return [0.0] * len(candidates)
    
    @staticmethod
    def cache_embeddings(embeddings: np.ndarray, filepath: str):
        """Cache embeddings to disk"""
        try:
            import joblib
            joblib.dump(embeddings, filepath)
            logger.info(f"Cached embeddings to {filepath}")
        except Exception as e:
            logger.error(f"Error caching embeddings: {e}")
    
    @staticmethod
    def load_cached_embeddings(filepath: str) -> Optional[np.ndarray]:
        """Load cached embeddings from disk"""
        try:
            import joblib
            embeddings = joblib.load(filepath)
            logger.info(f"Loaded cached embeddings from {filepath}")
            return embeddings
        except Exception as e:
            logger.error(f"Error loading cached embeddings: {e}")
            return None
