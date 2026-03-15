"""
Embedding Service Behaviour Tests

These tests document and verify the behaviour of the embedding service
which handles text embedding and vector store operations for RAG.

Behaviours Documented:
1. Text embedding: Generating vector representations of text
2. Work order embedding: Combining fields for semantic search
3. Vector store operations: Indexing and searching work orders
4. Similarity search: Finding semantically related content
"""

import pytest
from pathlib import Path

from app.services.embedding_service import EmbeddingService


# =============================================================================
# Text Embedding Behaviours
# =============================================================================

class TestTextEmbeddingBehaviour:
    """
    Text embedding generation behaviours.
    
    The embedding service converts text into numerical vectors that
    capture semantic meaning, enabling similarity search.
    """
    
    @pytest.fixture
    def embedding_service(self, temp_chroma_dir):
        """Create an isolated embedding service for testing."""
        return EmbeddingService(persist_directory=temp_chroma_dir)
    
    def test_embed_text_produces_vector(self, embedding_service):
        """
        Embedding text produces a list of floating point numbers.
        """
        text = "Annual oil change and filter replacement"
        embedding = embedding_service.embed_text(text)
        
        # Embedding should be a list of floats
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embedding_dimension_is_consistent(self, embedding_service):
        """
        All embeddings have the same dimensionality.
        
        The MiniLM model produces 384-dimensional embeddings.
        """
        texts = [
            "Oil change service",
            "Bottom paint and hull cleaning",
            "Winterization with antifreeze",
        ]
        
        embeddings = [embedding_service.embed_text(t) for t in texts]
        dimensions = [len(e) for e in embeddings]
        
        # All embeddings should have same dimension
        assert len(set(dimensions)) == 1
        # MiniLM produces 384-dim embeddings
        assert dimensions[0] == 384
    
    def test_similar_texts_have_similar_embeddings(self, embedding_service):
        """
        Semantically similar texts produce similar embeddings.
        
        This is the foundation of semantic search.
        """
        import math
        
        text1 = "Oil change and filter replacement"
        text2 = "Change oil and replace filter"  # Same meaning, different words
        text3 = "Hull cleaning and bottom paint"  # Different meaning
        
        emb1 = embedding_service.embed_text(text1)
        emb2 = embedding_service.embed_text(text2)
        emb3 = embedding_service.embed_text(text3)
        
        # Calculate cosine similarity
        def cosine_similarity(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            return dot / (norm_a * norm_b)
        
        sim_1_2 = cosine_similarity(emb1, emb2)
        sim_1_3 = cosine_similarity(emb1, emb3)
        
        # Similar texts should have higher similarity
        assert sim_1_2 > sim_1_3
    
    def test_batch_embedding_is_efficient(self, embedding_service):
        """
        Batch embedding multiple texts at once is supported.
        """
        texts = [
            "Oil change",
            "Winterization",
            "Hull cleaning",
            "Lower unit service",
        ]
        
        embeddings = embedding_service.embed_batch(texts)
        
        assert len(embeddings) == len(texts)
        assert all(len(e) == 384 for e in embeddings)


# =============================================================================
# Work Order Embedding Behaviours
# =============================================================================

class TestWorkOrderEmbeddingBehaviour:
    """
    Work order embedding combines multiple fields for richer matching.
    """
    
    @pytest.fixture
    def embedding_service(self, temp_chroma_dir):
        """Create an isolated embedding service for testing."""
        return EmbeddingService(persist_directory=temp_chroma_dir)
    
    def test_work_order_embedding_text_includes_key_fields(self, embedding_service, sample_work_order):
        """
        Work order embedding text combines service description, vessel, and engine.
        
        This allows matching on any of these dimensions.
        """
        embedding_text = embedding_service.create_work_order_embedding_text(sample_work_order)
        
        # Should include service description
        assert "Oil and filter change" in embedding_text
        # Should include vessel type
        assert "Cabin Cruiser" in embedding_text
        # Should include engine info
        assert "Volvo Penta" in embedding_text
        # Should include service category
        assert "engine" in embedding_text
    
    def test_work_order_embedding_text_format(self, embedding_service):
        """
        Embedding text follows a consistent format for all work orders.
        """
        work_order = {
            "service_description": "Winterization",
            "vessel_type": "Runabout",
            "loa_range": "20-25",
            "engine_make": "MerCruiser",
            "engine_model": "4.3L",
            "service_category": "annual",
        }
        
        embedding_text = embedding_service.create_work_order_embedding_text(work_order)
        
        # Format uses pipe separators
        assert "|" in embedding_text
        # Contains labeled sections
        assert "Service:" in embedding_text
        assert "Vessel:" in embedding_text
        assert "Engine:" in embedding_text


# =============================================================================
# Vector Store Indexing Behaviours
# =============================================================================

class TestVectorStoreIndexingBehaviour:
    """
    Vector store indexing and retrieval behaviours.
    """
    
    @pytest.fixture
    def embedding_service(self, temp_chroma_dir):
        """Create an isolated embedding service for testing."""
        return EmbeddingService(persist_directory=temp_chroma_dir)
    
    def test_index_single_work_order(self, embedding_service, sample_work_order):
        """
        A single work order can be indexed into the vector store.
        """
        initial_count = embedding_service.get_collection_count()
        
        embedding_service.index_work_order(sample_work_order)
        
        assert embedding_service.get_collection_count() == initial_count + 1
    
    def test_index_work_order_requires_id(self, embedding_service):
        """
        Work orders must have an ID to be indexed.
        """
        invalid_order = {
            "service_description": "Test",
            "vessel_type": "Test",
        }  # Missing work_order_id
        
        with pytest.raises(ValueError, match="work_order_id"):
            embedding_service.index_work_order(invalid_order)
    
    def test_batch_indexing_work_orders(self, embedding_service, sample_work_orders):
        """
        Multiple work orders can be indexed efficiently in batch.
        """
        count = embedding_service.index_work_orders_batch(sample_work_orders)
        
        assert count == len(sample_work_orders)
        assert embedding_service.get_collection_count() == len(sample_work_orders)
    
    def test_upsert_updates_existing_work_order(self, embedding_service, sample_work_order):
        """
        Indexing a work order with the same ID updates it.
        """
        # Index original
        embedding_service.index_work_order(sample_work_order)
        initial_count = embedding_service.get_collection_count()
        
        # Update and re-index
        updated_order = sample_work_order.copy()
        updated_order["service_description"] = "Updated service description"
        embedding_service.index_work_order(updated_order)
        
        # Count should remain the same (upsert, not insert)
        assert embedding_service.get_collection_count() == initial_count


# =============================================================================
# Similarity Search Behaviours
# =============================================================================

class TestSimilaritySearchBehaviour:
    """
    Similarity search behaviours for finding related work orders.
    """
    
    @pytest.fixture
    def indexed_service(self, temp_chroma_dir, sample_work_orders):
        """Create an embedding service with indexed work orders."""
        service = EmbeddingService(persist_directory=temp_chroma_dir)
        service.index_work_orders_batch(sample_work_orders)
        return service
    
    def test_search_returns_results(self, indexed_service):
        """
        Searching returns matching work orders.
        """
        results = indexed_service.search("oil change", n_results=5)
        
        assert results is not None
        assert "ids" in results
        assert len(results["ids"]) > 0
    
    def test_search_returns_distances(self, indexed_service):
        """
        Search results include distance scores for ranking.
        """
        results = indexed_service.search("oil change", n_results=5)
        
        assert "distances" in results
        # Distances should be present for each result
        assert len(results["distances"][0]) == len(results["ids"][0])
    
    def test_search_returns_metadata(self, indexed_service):
        """
        Search results include work order metadata.
        """
        results = indexed_service.search("oil change", n_results=5)
        
        assert "metadatas" in results
        metadata = results["metadatas"][0][0]
        
        # Metadata should include key fields
        assert "work_order_id" in metadata
        assert "engine_make" in metadata
        assert "service_description" in metadata
    
    def test_search_can_filter_by_engine_make(self, indexed_service):
        """
        Search supports filtering by engine make.
        """
        results = indexed_service.search(
            "service",
            n_results=10,
            where={"engine_make": {"$eq": "Volvo Penta"}}
        )
        
        # All results should be Volvo Penta
        for metadata in results["metadatas"][0]:
            assert metadata["engine_make"] == "Volvo Penta"
    
    def test_search_limits_results(self, indexed_service):
        """
        Search respects the n_results limit.
        """
        results = indexed_service.search("service", n_results=2)
        
        assert len(results["ids"][0]) <= 2
    
    def test_relevant_results_rank_higher(self, indexed_service):
        """
        More relevant results have lower distances (rank higher).
        """
        # Search for something specific
        results = indexed_service.search("oil and filter change", n_results=3)
        
        distances = results["distances"][0]
        
        # Distances should be sorted ascending (most similar first)
        for i in range(len(distances) - 1):
            assert distances[i] <= distances[i + 1]


# =============================================================================
# Collection Management Behaviours
# =============================================================================

class TestCollectionManagementBehaviour:
    """
    Vector store collection management behaviours.
    """
    
    def test_collection_is_created_on_first_access(self, temp_chroma_dir):
        """
        The work_orders collection is created automatically.
        """
        service = EmbeddingService(persist_directory=temp_chroma_dir)
        
        # Accessing collection creates it
        collection = service.collection
        
        assert collection is not None
        assert collection.name == "work_orders"
    
    def test_reset_clears_all_data(self, temp_chroma_dir, sample_work_orders):
        """
        Reset removes all indexed work orders.
        """
        service = EmbeddingService(persist_directory=temp_chroma_dir)
        service.index_work_orders_batch(sample_work_orders)
        
        assert service.get_collection_count() > 0
        
        service.reset()
        
        assert service.get_collection_count() == 0
    
    def test_persistence_survives_restart(self, temp_chroma_dir, sample_work_orders):
        """
        Indexed data persists across service restarts.
        """
        # Index with first service instance
        service1 = EmbeddingService(persist_directory=temp_chroma_dir)
        service1.index_work_orders_batch(sample_work_orders)
        original_count = service1.get_collection_count()
        
        # Create new service instance pointing to same directory
        service2 = EmbeddingService(persist_directory=temp_chroma_dir)
        
        assert service2.get_collection_count() == original_count
