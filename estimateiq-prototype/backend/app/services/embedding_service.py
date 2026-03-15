"""
EstimateIQ Embedding Service

Handles text embedding for the RAG system using sentence-transformers.
Embeddings are used to find semantically similar work orders.
"""

from typing import List, Optional
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """
    Service for generating text embeddings and managing the vector store.
    
    Uses sentence-transformers for local embedding generation (no API needed).
    Uses ChromaDB for persistent vector storage and similarity search.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            persist_directory: Optional path to persist ChromaDB data.
                             Defaults to settings.chroma_persist_dir
        """
        self.persist_directory = persist_directory or settings.chroma_persist_dir
        
        # Initialize sentence transformer model
        # all-MiniLM-L6-v2 is a good balance of speed and quality for semantic search
        self._model: Optional[SentenceTransformer] = None
        
        # Initialize ChromaDB client with persistence
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None
        
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model"""
        if self._model is None:
            print(f"Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model
    
    @property
    def client(self) -> chromadb.PersistentClient:
        """Lazy load the ChromaDB client"""
        if self._client is None:
            print(f"Initializing ChromaDB at: {self.persist_directory}")
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        return self._client
    
    @property
    def collection(self):
        """Get or create the work_orders collection"""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="work_orders",
                metadata={"description": "Historical marine service work orders for RAG retrieval"}
            )
        return self._collection
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text string.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient than individual calls).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def create_work_order_embedding_text(self, work_order: dict) -> str:
        """
        Create a combined text representation of a work order for embedding.
        
        Combines key fields that are relevant for semantic similarity matching:
        - Service description (most important)
        - Vessel type
        - Engine make and model
        - Service category
        
        Args:
            work_order: Dictionary containing work order data
            
        Returns:
            Combined text suitable for embedding
        """
        parts = [
            f"Service: {work_order.get('service_description', '')}",
            f"Vessel: {work_order.get('vessel_type', '')}",
            f"Length: {work_order.get('loa_range', '')} feet",
            f"Engine: {work_order.get('engine_make', '')} {work_order.get('engine_model', '')}",
            f"Category: {work_order.get('service_category', '')}",
        ]
        return " | ".join(parts)
    
    def index_work_order(self, work_order: dict) -> None:
        """
        Index a single work order into the vector store.
        
        Args:
            work_order: Dictionary containing work order data
        """
        work_order_id = work_order.get("work_order_id")
        if not work_order_id:
            raise ValueError("Work order must have a work_order_id")
        
        # Create embedding text
        embedding_text = self.create_work_order_embedding_text(work_order)
        
        # Generate embedding
        embedding = self.embed_text(embedding_text)
        
        # Store in ChromaDB
        self.collection.upsert(
            ids=[work_order_id],
            embeddings=[embedding],
            documents=[embedding_text],
            metadatas=[{
                "work_order_id": work_order_id,
                "vessel_type": work_order.get("vessel_type", ""),
                "loa": float(work_order.get("loa", 0)),
                "loa_range": work_order.get("loa_range", ""),
                "year": int(work_order.get("year", 0)),
                "engine_make": work_order.get("engine_make", ""),
                "engine_model": work_order.get("engine_model", ""),
                "service_category": work_order.get("service_category", ""),
                "service_description": work_order.get("service_description", ""),
                "total_labor_hours": float(work_order.get("total_labor_hours", 0)),
                "total_parts_cost": float(work_order.get("total_parts_cost", 0)),
                "total_invoice": float(work_order.get("total_invoice", 0)),
                "region": work_order.get("region", ""),
                "season": work_order.get("season", ""),
                "completion_date": work_order.get("completion_date", ""),
            }]
        )
    
    def index_work_orders_batch(self, work_orders: List[dict]) -> int:
        """
        Index multiple work orders efficiently in batch.
        
        Args:
            work_orders: List of work order dictionaries
            
        Returns:
            Number of work orders indexed
        """
        if not work_orders:
            return 0
        
        ids = []
        embedding_texts = []
        metadatas = []
        
        for wo in work_orders:
            work_order_id = wo.get("work_order_id")
            if not work_order_id:
                continue
                
            ids.append(work_order_id)
            embedding_texts.append(self.create_work_order_embedding_text(wo))
            metadatas.append({
                "work_order_id": work_order_id,
                "vessel_type": wo.get("vessel_type", ""),
                "loa": float(wo.get("loa", 0)),
                "loa_range": wo.get("loa_range", ""),
                "year": int(wo.get("year", 0)),
                "engine_make": wo.get("engine_make", ""),
                "engine_model": wo.get("engine_model", ""),
                "service_category": wo.get("service_category", ""),
                "service_description": wo.get("service_description", ""),
                "total_labor_hours": float(wo.get("total_labor_hours", 0)),
                "total_parts_cost": float(wo.get("total_parts_cost", 0)),
                "total_invoice": float(wo.get("total_invoice", 0)),
                "region": wo.get("region", ""),
                "season": wo.get("season", ""),
                "completion_date": wo.get("completion_date", ""),
            })
        
        # Generate embeddings in batch
        embeddings = self.embed_batch(embedding_texts)
        
        # Upsert all at once
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=embedding_texts,
            metadatas=metadatas
        )
        
        return len(ids)
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[dict] = None
    ) -> dict:
        """
        Search for similar work orders using semantic similarity.
        
        Args:
            query: The search query text
            n_results: Maximum number of results to return
            where: Optional filter conditions (e.g., {"engine_make": "Volvo Penta"})
            
        Returns:
            ChromaDB query results containing ids, distances, documents, and metadatas
        """
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()
    
    def delete_collection(self) -> None:
        """Delete the work_orders collection (use with caution)"""
        self.client.delete_collection("work_orders")
        self._collection = None
    
    def reset(self) -> None:
        """Reset the collection by deleting and recreating it"""
        try:
            self.delete_collection()
        except Exception:
            pass  # Collection might not exist
        # Will be recreated on next access
        self._collection = None


# Global singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
