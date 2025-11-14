"""
Model service for loading and using the BERT model and Annoy index.
"""
import os
import pickle
from pathlib import Path
from typing import List

import numpy as np
import onnxruntime as ort
from annoy import AnnoyIndex
from tokenizers import Tokenizer
from fastapi import HTTPException

from app.core.config import settings


class ModelService:
    """
    Service for loading and using the BERT model and Annoy index.
    """
    
    def __init__(
        self,
        model_path: Path,
        index_path: Path,
        movies_map_path: Path,
    ):
        """
        Initialize the model service.
        
        Args:
            model_path: Path to the ONNX model file
            index_path: Path to the Annoy index file
            movies_map_path: Path to the movies mapping pickle file
        """
        self.model_path = model_path
        self.index_path = index_path
        self.movies_map_path = movies_map_path
        
        self.session: ort.InferenceSession | None = None
        self.tokenizer: Tokenizer | None = None
        self.index: AnnoyIndex | None = None
        self.movies_map: dict | None = None
        self._is_loaded = False
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._is_loaded
    
    def load(self) -> None:
        """Load the model, tokenizer, index, and movies map."""
        try:
            # Load ONNX model with memory optimizations for Render (512MB limit)
            print(f"Loading ONNX model from {self.model_path}")
            
            # Configure session options to minimize memory usage for Render's 512MB limit
            session_options = ort.SessionOptions()
            session_options.enable_cpu_mem_arena = False  # Disable memory arena to reduce memory footprint (~30-50MB saved)
            session_options.enable_mem_pattern = False  # Disable memory pattern optimization (uses less memory)
            
            # Use sequential execution mode to reduce memory usage (vs parallel)
            # Note: This may be slightly slower but uses significantly less memory
            try:
                # Try to set execution mode to sequential (reduces memory)
                session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            except (AttributeError, TypeError):
                # ExecutionMode not available in this version, skip
                pass
            
            # Use basic graph optimization (vs full optimization which uses more memory)
            try:
                # Try to set basic optimization level (reduces memory overhead)
                session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
            except (AttributeError, TypeError):
                # GraphOptimizationLevel not available in this version, use default
                pass
            
            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=session_options,
                providers=["CPUExecutionProvider"],
            )
            
            # Load tokenizer
            tokenizer_path = self.model_path.parent / "tokenizer.json"
            if not tokenizer_path.exists():
                raise FileNotFoundError(f"Tokenizer not found at {tokenizer_path}")
            
            print(f"Loading tokenizer from {tokenizer_path}")
            self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
            
            # Load Annoy index
            print(f"Loading Annoy index from {self.index_path}")
            if not self.index_path.exists():
                raise FileNotFoundError(f"Index not found at {self.index_path}")
            
            self.index = AnnoyIndex(settings.EMBEDDING_SIZE, "angular")
            self.index.load(str(self.index_path))
            
            # Load movies map
            print(f"Loading movies map from {self.movies_map_path}")
            if not self.movies_map_path.exists():
                raise FileNotFoundError(f"Movies map not found at {self.movies_map_path}")
            
            with open(self.movies_map_path, "rb") as f:
                self.movies_map = pickle.load(f)
            
            self._is_loaded = True
            print("All components loaded successfully!")
        
        except Exception as e:
            print(f"Error loading components: {e}")
            raise
    
    def _encode_text(self, text: str) -> np.ndarray:
        """
        Encode text using the BERT model.
        
        Args:
            text: Input text to encode
            
        Returns:
            Embedding vector
        """
        if self.session is None or self.tokenizer is None:
            raise ValueError("Model or tokenizer not loaded")
        
        # Tokenize text
        encoding = self.tokenizer.encode(text)
        input_ids = np.array([encoding.ids], dtype=np.int64)
        attention_mask = np.array([encoding.attention_mask], dtype=np.int64)
        
        # Get input names from the model
        input_names = [input.name for input in self.session.get_inputs()]
        
        # Prepare inputs in the correct order
        inputs = {}
        for name in input_names:
            if "input_ids" in name.lower():
                inputs[name] = input_ids
            elif "attention" in name.lower() or "mask" in name.lower():
                inputs[name] = attention_mask
        
        # Run inference
        outputs = self.session.run(None, inputs)
        
        # Extract embedding (mean pooling of last hidden state)
        last_hidden_state = outputs[0]  # Shape: [batch_size, seq_len, hidden_size]
        attention_mask_expanded = np.expand_dims(attention_mask, axis=-1)
        
        # Mean pooling with attention mask
        sum_embeddings = np.sum(last_hidden_state * attention_mask_expanded, axis=1)
        sum_mask = np.sum(attention_mask_expanded, axis=1)
        embedding = sum_embeddings / sum_mask
        
        # Normalize
        norm = np.linalg.norm(embedding, axis=1, keepdims=True)
        norm = np.where(norm == 0, 1, norm)  # Avoid division by zero
        embedding = embedding / norm
        
        return embedding[0]  # Return first (and only) embedding
    
    def recommend(
        self,
        synopsis: str,
        top_k: int = 10,
    ) -> List[dict]:
        """
        Get movie recommendations based on synopsis.
        
        Args:
            synopsis: Movie synopsis
            top_k: Number of recommendations to return
            
        Returns:
            List of recommendation dictionaries with movie_id, similarity_score, title, and overview
        """
        if not self.is_loaded:
            raise ValueError("Model not loaded")
        
        if not synopsis or len(synopsis.strip()) < 10:
            raise ValueError("Synopsis must be at least 10 characters long")
        
        # Encode the synopsis
        query_embedding = self._encode_text(synopsis)
        
        # Search in Annoy index
        if self.index is None:
            raise ValueError("Index not loaded")
        
        # Get nearest neighbors (top_k + 1 to account for potential self-match)
        neighbors, distances = self.index.get_nns_by_vector(
            query_embedding.tolist(),
            n=top_k,
            include_distances=True,
        )
        
        # Convert distances to similarity scores (angular distance -> cosine similarity)
        # Angular distance = arccos(cosine_similarity)
        # So: similarity = 1 - (angular_distance / pi)
        similarity_scores = [1 - (d / np.pi) for d in distances]
        
        # Build recommendations
        recommendations = []
        for movie_id, similarity in zip(neighbors, similarity_scores):
            movie_data = {
                "movie_id": int(movie_id),
                "similarity_score": float(similarity),
            }
            
            # Add title and overview if available in movies_map
            if self.movies_map is not None and movie_id in self.movies_map:
                movie_info = self.movies_map[movie_id]
                if isinstance(movie_info, dict):
                    movie_data["title"] = movie_info.get("title")
                    movie_data["overview"] = movie_info.get("overview")
                else:
                    movie_data["title"] = str(movie_info) if movie_info else None
            
            recommendations.append(movie_data)
        
        return recommendations


# Global model service instance (will be set on startup)
_model_service: ModelService | None = None


def get_model_service() -> ModelService:
    """Dependency to get the model service instance."""
    if _model_service is None:
        raise HTTPException(
            status_code=503,
            detail="Model service is not available",
        )
    return _model_service


def get_model_service_instance() -> ModelService | None:
    """Get the model service instance (for internal use)."""
    return _model_service


def set_model_service(service: ModelService) -> None:
    """Set the global model service instance."""
    global _model_service
    _model_service = service

