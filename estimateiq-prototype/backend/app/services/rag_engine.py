"""
EstimateIQ RAG Engine

Retrieval-Augmented Generation engine for finding similar historical work orders
and building context for estimate generation.
"""

import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.core.config import settings
from app.services.embedding_service import get_embedding_service, EmbeddingService
from app.models import Vessel, SimilarJob, HistoricalWorkOrder


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for EstimateIQ.
    
    This engine:
    1. Accepts service descriptions and vessel specifications
    2. Retrieves semantically similar historical work orders
    3. Filters by relevant criteria (engine make, vessel size, etc.)
    4. Calculates confidence scores based on match quality
    5. Returns ranked results for estimate generation
    """
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize the RAG engine.
        
        Args:
            embedding_service: Optional custom embedding service.
                             Defaults to the global singleton.
        """
        self._embedding_service = embedding_service
        self._work_orders_cache: Optional[Dict[str, dict]] = None
    
    @property
    def embedding_service(self) -> EmbeddingService:
        """Get the embedding service (lazy loaded)"""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service
    
    def _load_work_orders_cache(self) -> Dict[str, dict]:
        """Load and cache all work orders for quick access to full details"""
        if self._work_orders_cache is None:
            work_orders_path = settings.data_dir / settings.work_orders_file
            with open(work_orders_path, 'r') as f:
                work_orders = json.load(f)
            self._work_orders_cache = {wo['work_order_id']: wo for wo in work_orders}
        return self._work_orders_cache
    
    def retrieve_similar_jobs(
        self,
        service_description: str,
        vessel: Optional[Vessel] = None,
        top_k: int = 10,
        engine_make_filter: Optional[str] = None,
        loa_min: Optional[float] = None,
        loa_max: Optional[float] = None,
        service_category_filter: Optional[str] = None,
    ) -> List[SimilarJob]:
        """
        Retrieve similar historical work orders based on semantic similarity.
        
        Args:
            service_description: The service request description to match against
            vessel: Optional vessel specifications for filtering
            top_k: Maximum number of results to return
            engine_make_filter: Optional filter by engine make
            loa_min: Optional minimum vessel length
            loa_max: Optional maximum vessel length
            service_category_filter: Optional filter by service category
            
        Returns:
            List of SimilarJob objects ranked by similarity
        """
        # Build the search query with context
        if vessel:
            query = f"Service: {service_description} | Engine: {vessel.engine_make} {vessel.engine_model}"
        else:
            query = service_description
        
        # Build filter conditions for ChromaDB
        where_conditions = self._build_where_conditions(
            engine_make=engine_make_filter or (vessel.engine_make if vessel else None),
            loa_min=loa_min,
            loa_max=loa_max,
            service_category=service_category_filter,
        )
        
        # Perform the search
        # Note: We request more results than top_k to allow for post-filtering
        search_results = self.embedding_service.search(
            query=query,
            n_results=min(top_k * 2, 50),  # Request more for filtering margin
            where=where_conditions
        )
        
        # Convert to SimilarJob objects
        similar_jobs = self._convert_results_to_similar_jobs(search_results, vessel)
        
        # Apply additional filtering and scoring
        similar_jobs = self._apply_vessel_scoring(similar_jobs, vessel)
        
        # Sort by final similarity score and limit to top_k
        similar_jobs.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return similar_jobs[:top_k]
    
    def _build_where_conditions(
        self,
        engine_make: Optional[str] = None,
        loa_min: Optional[float] = None,
        loa_max: Optional[float] = None,
        service_category: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Build ChromaDB where conditions for filtering.
        
        Note: ChromaDB has limited filter capabilities, so complex filters
        may need to be applied post-retrieval.
        """
        conditions = []
        
        if engine_make:
            # Case-insensitive partial match isn't directly supported,
            # so we'll filter post-retrieval for exact matches
            conditions.append({"engine_make": {"$eq": engine_make}})
        
        if service_category:
            conditions.append({"service_category": {"$eq": service_category}})
        
        # LOA range filters
        if loa_min is not None:
            conditions.append({"loa": {"$gte": loa_min}})
        if loa_max is not None:
            conditions.append({"loa": {"$lte": loa_max}})
        
        # Combine conditions with AND
        if len(conditions) == 0:
            return None
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {"$and": conditions}
    
    def _convert_results_to_similar_jobs(
        self,
        search_results: dict,
        vessel: Optional[Vessel] = None
    ) -> List[SimilarJob]:
        """Convert ChromaDB search results to SimilarJob objects"""
        similar_jobs = []
        
        if not search_results or not search_results.get('ids'):
            return similar_jobs
        
        ids = search_results['ids'][0] if search_results['ids'] else []
        distances = search_results['distances'][0] if search_results.get('distances') else []
        metadatas = search_results['metadatas'][0] if search_results.get('metadatas') else []
        
        # Load full work order data for additional details
        work_orders_cache = self._load_work_orders_cache()
        
        for idx, (work_order_id, distance) in enumerate(zip(ids, distances)):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            
            # ChromaDB returns L2 (Euclidean) distance by default
            # Lower distance = higher similarity
            # For normalized embeddings, L2 distance range is [0, 2]
            # We convert to similarity: sim = 1 / (1 + distance) which gives range (0, 1]
            # Alternatively: sim = max(0, 1 - distance/2) for linear mapping
            # Using exponential decay for smoother scores:
            similarity_score = 1 / (1 + distance)
            
            # Get full work order data if available
            full_wo = work_orders_cache.get(work_order_id, {})
            
            similar_job = SimilarJob(
                work_order_id=work_order_id,
                similarity_score=round(similarity_score, 4),
                vessel_type=metadata.get('vessel_type', full_wo.get('vessel_type', '')),
                loa=float(metadata.get('loa', full_wo.get('loa', 0))),
                engine=f"{metadata.get('engine_make', '')} {metadata.get('engine_model', '')}".strip(),
                service_description=metadata.get('service_description', full_wo.get('service_description', '')),
                total_labor_hours=float(metadata.get('total_labor_hours', full_wo.get('total_labor_hours', 0))),
                total_invoice=float(metadata.get('total_invoice', full_wo.get('total_invoice', 0))),
                completion_date=metadata.get('completion_date', full_wo.get('completion_date', '')),
            )
            similar_jobs.append(similar_job)
        
        return similar_jobs
    
    def _apply_vessel_scoring(
        self,
        similar_jobs: List[SimilarJob],
        vessel: Optional[Vessel]
    ) -> List[SimilarJob]:
        """
        Apply additional scoring based on vessel match quality.
        
        Boosts similarity scores for jobs that match vessel characteristics.
        """
        if not vessel:
            return similar_jobs
        
        for job in similar_jobs:
            boost = 0.0
            
            # Engine make match boost
            if vessel.engine_make.lower() in job.engine.lower():
                boost += 0.05
                
                # Engine model match boost (additional)
                if vessel.engine_model.lower() in job.engine.lower():
                    boost += 0.05
            
            # LOA proximity boost (within 5 feet = full boost, decreases linearly)
            if job.loa > 0:
                loa_diff = abs(vessel.loa - job.loa)
                if loa_diff <= 5:
                    boost += 0.03 * (1 - loa_diff / 5)
            
            # Apply boost (cap at 1.0)
            job.similarity_score = min(1.0, job.similarity_score + boost)
        
        return similar_jobs
    
    def get_similar_jobs_summary(
        self,
        similar_jobs: List[SimilarJob],
        vessel: Optional[Vessel] = None
    ) -> str:
        """
        Generate a human-readable summary of similar jobs found.
        
        Example: "Based on 15 similar oil changes on 25-30' vessels with Volvo D4 engines"
        """
        if not similar_jobs:
            return "No similar historical jobs found"
        
        count = len(similar_jobs)
        
        # Analyze common patterns
        engine_makes = {}
        loa_ranges = {}
        
        for job in similar_jobs:
            # Count engine makes
            engine_make = job.engine.split()[0] if job.engine else "Unknown"
            engine_makes[engine_make] = engine_makes.get(engine_make, 0) + 1
            
            # Count LOA ranges
            loa_range = self._get_loa_range(job.loa)
            loa_ranges[loa_range] = loa_ranges.get(loa_range, 0) + 1
        
        # Get most common patterns
        most_common_engine = max(engine_makes, key=engine_makes.get) if engine_makes else ""
        most_common_loa = max(loa_ranges, key=loa_ranges.get) if loa_ranges else ""
        
        # Build summary
        if vessel:
            return f"Based on {count} similar jobs on {most_common_loa}' vessels with {vessel.engine_make} engines"
        else:
            return f"Based on {count} similar jobs on {most_common_loa}' vessels with {most_common_engine} engines"
    
    def _get_loa_range(self, loa: float) -> str:
        """Convert LOA to a range string"""
        if loa < 20:
            return "15-20"
        elif loa < 25:
            return "20-25"
        elif loa < 30:
            return "25-30"
        elif loa < 35:
            return "30-35"
        elif loa < 40:
            return "35-40"
        else:
            return "40+"
    
    def calculate_confidence_score(
        self,
        similar_jobs: List[SimilarJob],
        vessel: Optional[Vessel] = None
    ) -> float:
        """
        Calculate overall confidence score for an estimate.
        
        Based on:
        - Number of similar jobs found (30%)
        - Average similarity score of top jobs (30%)
        - Variance in labor hours across similar jobs (20%)
        - Vessel specification match quality (20%)
        
        Formula from design document:
        confidence = (
            0.3 * (min(similar_job_count, 20) / 20) +
            0.3 * avg_similarity_score +
            0.2 * (1 - labor_variance_normalized) +
            0.2 * vessel_match_score
        )
        """
        if not similar_jobs:
            return 0.3  # Base confidence for no matches
        
        # Factor 1: Similar job count (more = higher confidence)
        count_score = min(len(similar_jobs), 20) / 20
        
        # Factor 2: Average similarity score
        avg_similarity = sum(job.similarity_score for job in similar_jobs) / len(similar_jobs)
        
        # Factor 3: Labor variance (lower = higher confidence)
        labor_hours = [job.total_labor_hours for job in similar_jobs if job.total_labor_hours > 0]
        if len(labor_hours) > 1:
            mean_labor = sum(labor_hours) / len(labor_hours)
            variance = sum((h - mean_labor) ** 2 for h in labor_hours) / len(labor_hours)
            std_dev = variance ** 0.5
            # Normalize: assume std_dev > 5 hours is very high variance
            labor_variance_normalized = min(std_dev / 5, 1.0)
        else:
            labor_variance_normalized = 0.5  # Neutral if not enough data
        
        # Factor 4: Vessel match quality
        vessel_match_score = 0.5  # Default neutral
        if vessel and similar_jobs:
            matches = sum(
                1 for job in similar_jobs 
                if vessel.engine_make.lower() in job.engine.lower()
            )
            vessel_match_score = matches / len(similar_jobs)
        
        # Calculate final confidence
        confidence = (
            0.3 * count_score +
            0.3 * avg_similarity +
            0.2 * (1 - labor_variance_normalized) +
            0.2 * vessel_match_score
        )
        
        return round(min(max(confidence, 0.0), 1.0), 4)
    
    def get_full_work_order(self, work_order_id: str) -> Optional[dict]:
        """
        Get the full work order data by ID.
        
        Args:
            work_order_id: The work order ID to look up
            
        Returns:
            Full work order dictionary or None if not found
        """
        work_orders_cache = self._load_work_orders_cache()
        return work_orders_cache.get(work_order_id)
    
    def get_labor_statistics(
        self,
        similar_jobs: List[SimilarJob]
    ) -> Dict[str, float]:
        """
        Calculate labor hour statistics from similar jobs.
        
        Returns:
            Dict with 'min', 'max', 'mean', 'median' labor hours
        """
        labor_hours = [job.total_labor_hours for job in similar_jobs if job.total_labor_hours > 0]
        
        if not labor_hours:
            return {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
        
        labor_hours.sort()
        
        return {
            'min': labor_hours[0],
            'max': labor_hours[-1],
            'mean': sum(labor_hours) / len(labor_hours),
            'median': labor_hours[len(labor_hours) // 2],
        }
    
    def get_parts_patterns(
        self,
        work_order_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Analyze parts usage patterns from similar work orders.
        
        Returns commonly used parts across the given work orders.
        """
        work_orders_cache = self._load_work_orders_cache()
        
        parts_count = {}
        
        for wo_id in work_order_ids:
            wo = work_orders_cache.get(wo_id, {})
            for part in wo.get('parts_used', []):
                part_num = part.get('part_number', '')
                if part_num not in parts_count:
                    parts_count[part_num] = {
                        'part_number': part_num,
                        'description': part.get('description', ''),
                        'count': 0,
                        'total_quantity': 0,
                        'avg_price': 0,
                        'prices': [],
                    }
                parts_count[part_num]['count'] += 1
                parts_count[part_num]['total_quantity'] += part.get('quantity', 0)
                parts_count[part_num]['prices'].append(part.get('unit_price', 0))
        
        # Calculate averages and sort by frequency
        result = []
        for part_num, data in parts_count.items():
            if data['prices']:
                data['avg_price'] = sum(data['prices']) / len(data['prices'])
            data['avg_quantity'] = data['total_quantity'] / data['count'] if data['count'] > 0 else 0
            del data['prices']  # Remove raw prices
            result.append(data)
        
        # Sort by frequency (most common first)
        result.sort(key=lambda x: x['count'], reverse=True)
        
        return result


# Global singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get the global RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
