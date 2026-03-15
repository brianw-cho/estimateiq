#!/usr/bin/env python3
"""
Build Vector Store Script

This script indexes all historical work orders from the JSON data file
into the ChromaDB vector store for RAG retrieval.

Usage:
    cd backend
    python -m scripts.build_vector_store

Or with the virtual environment activated:
    python scripts/build_vector_store.py
"""

import sys
import json
from pathlib import Path

# Add the backend directory to the path so we can import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.services.embedding_service import get_embedding_service


def load_work_orders() -> list:
    """Load work orders from the JSON data file"""
    work_orders_path = settings.data_dir / settings.work_orders_file
    
    print(f"Loading work orders from: {work_orders_path}")
    
    if not work_orders_path.exists():
        raise FileNotFoundError(f"Work orders file not found: {work_orders_path}")
    
    with open(work_orders_path, 'r') as f:
        work_orders = json.load(f)
    
    print(f"Loaded {len(work_orders)} work orders")
    return work_orders


def build_vector_store(reset: bool = False):
    """
    Build the vector store by indexing all work orders.
    
    Args:
        reset: If True, delete existing collection before rebuilding
    """
    # Get the embedding service
    embedding_service = get_embedding_service()
    
    # Reset collection if requested
    if reset:
        print("Resetting vector store collection...")
        embedding_service.reset()
    
    # Check current count
    current_count = embedding_service.get_collection_count()
    print(f"Current documents in collection: {current_count}")
    
    # Load work orders
    work_orders = load_work_orders()
    
    # Index in batches for better performance
    batch_size = 50
    total_indexed = 0
    
    print(f"\nIndexing work orders in batches of {batch_size}...")
    
    for i in range(0, len(work_orders), batch_size):
        batch = work_orders[i:i + batch_size]
        indexed = embedding_service.index_work_orders_batch(batch)
        total_indexed += indexed
        print(f"  Indexed batch {i//batch_size + 1}: {indexed} documents (total: {total_indexed})")
    
    # Verify final count
    final_count = embedding_service.get_collection_count()
    print(f"\nVector store build complete!")
    print(f"Total documents in collection: {final_count}")
    
    return final_count


def test_search():
    """Run a quick test search to verify the vector store is working"""
    from app.services.rag_engine import get_rag_engine
    
    rag_engine = get_rag_engine()
    
    print("\n" + "="*60)
    print("Running test searches using RAG Engine...")
    print("="*60)
    
    test_queries = [
        "oil change and filter replacement",
        "bottom paint and hull cleaning",
        "engine won't start electrical issue",
        "winterization service",
        "lower unit service outboard",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        similar_jobs = rag_engine.retrieve_similar_jobs(
            service_description=query,
            top_k=3
        )
        
        if similar_jobs:
            for idx, job in enumerate(similar_jobs):
                print(f"  {idx+1}. [sim: {job.similarity_score:.3f}] {job.service_description}")
                print(f"     Vessel: {job.vessel_type} | Engine: {job.engine}")
                print(f"     Labor: {job.total_labor_hours:.1f}h | Invoice: ${job.total_invoice:.2f}")
        else:
            print("  No results found")
        
        # Show confidence score
        confidence = rag_engine.calculate_confidence_score(similar_jobs)
        summary = rag_engine.get_similar_jobs_summary(similar_jobs)
        print(f"  Confidence: {confidence:.1%} | {summary}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build the EstimateIQ vector store")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset the collection before building"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test searches after building"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("EstimateIQ Vector Store Builder")
    print("="*60)
    print()
    
    # Build the vector store
    build_vector_store(reset=args.reset)
    
    # Run test searches if requested
    if args.test:
        test_search()
    
    print("\nDone!")
