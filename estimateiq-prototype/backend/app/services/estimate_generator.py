"""
EstimateIQ Estimate Generator Service

Main orchestration service that brings together:
- RAG Engine (similar job retrieval)
- Mock LLM Service (template-based generation)
- Parts Catalog Service (parts validation and pricing)

This service is the primary entry point for generating estimates.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from app.core.config import settings
from app.core.mock_llm import MockLLMService, get_mock_llm_service
from app.services.rag_engine import RAGEngine, get_rag_engine
from app.services.parts_catalog import PartsCatalogService, get_parts_catalog_service
from app.models import (
    ServiceRequest,
    Vessel,
    Estimate,
    EstimateLineItem,
    EstimateRange,
    EstimateStatus,
    LineType,
    SimilarJob,
)


class EstimateGenerator:
    """
    Main estimate generation orchestrator.
    
    Coordinates the estimate generation workflow:
    1. Retrieve similar jobs from RAG engine
    2. Generate recommendations from mock LLM
    3. Validate and price parts from catalog
    4. Calculate confidence scores
    5. Assemble final estimate
    """
    
    def __init__(
        self,
        rag_engine: Optional[RAGEngine] = None,
        mock_llm: Optional[MockLLMService] = None,
        parts_catalog: Optional[PartsCatalogService] = None
    ):
        """
        Initialize the estimate generator.
        
        Args:
            rag_engine: Optional custom RAG engine. Defaults to global singleton.
            mock_llm: Optional custom mock LLM. Defaults to global singleton.
            parts_catalog: Optional custom parts catalog. Defaults to global singleton.
        """
        self._rag_engine = rag_engine
        self._mock_llm = mock_llm
        self._parts_catalog = parts_catalog
    
    @property
    def rag_engine(self) -> RAGEngine:
        """Get the RAG engine (lazy loaded)"""
        if self._rag_engine is None:
            self._rag_engine = get_rag_engine()
        return self._rag_engine
    
    @property
    def mock_llm(self) -> MockLLMService:
        """Get the mock LLM service (lazy loaded)"""
        if self._mock_llm is None:
            self._mock_llm = get_mock_llm_service()
        return self._mock_llm
    
    @property
    def parts_catalog(self) -> PartsCatalogService:
        """Get the parts catalog service (lazy loaded)"""
        if self._parts_catalog is None:
            self._parts_catalog = get_parts_catalog_service()
        return self._parts_catalog
    
    def generate_estimate(self, request: ServiceRequest) -> Estimate:
        """
        Generate a complete estimate from a service request.
        
        This is the main entry point for estimate generation.
        
        Args:
            request: The service request with vessel and description
            
        Returns:
            Complete Estimate object ready for display/editing
        """
        # Generate unique estimate ID
        estimate_id = f"est_{uuid.uuid4().hex[:12]}"
        
        # Step 1: Retrieve similar historical jobs
        similar_jobs = self._retrieve_similar_jobs(request)
        
        # Step 2: Get parts patterns from similar jobs
        parts_patterns = self._get_parts_patterns(similar_jobs)
        
        # Step 3: Generate estimate using mock LLM
        recommendation = self.mock_llm.generate_estimate(
            service_description=request.description,
            vessel=request.vessel,
            similar_jobs=similar_jobs,
            service_category=request.service_category.value if request.service_category else None,
            region=request.region or "Northeast"
        )
        
        # Step 4: Build labor line items
        labor_items = self._build_labor_items(recommendation, similar_jobs)
        
        # Step 5: Build parts line items (validated against catalog)
        parts_items = self._build_parts_items(
            recommendation=recommendation,
            vessel=request.vessel,
            parts_patterns=parts_patterns
        )
        
        # Step 6: Calculate totals
        labor_subtotal = sum(item.total_price for item in labor_items)
        parts_subtotal = sum(item.total_price for item in parts_items)
        total_estimate = labor_subtotal + parts_subtotal
        
        # Step 7: Calculate confidence score
        confidence_score = self._calculate_confidence(
            recommendation=recommendation,
            similar_jobs=similar_jobs,
            vessel=request.vessel
        )
        
        # Step 8: Calculate estimate range
        low, expected, high = self.mock_llm.calculate_estimate_range(
            base_total=total_estimate,
            confidence=confidence_score,
            similar_jobs=similar_jobs
        )
        
        estimate_range = EstimateRange(
            low=low,
            expected=expected,
            high=high
        )
        
        # Step 9: Generate similar jobs summary
        similar_jobs_summary = self.rag_engine.get_similar_jobs_summary(
            similar_jobs,
            request.vessel
        )
        
        # Build and return the complete estimate
        return Estimate(
            estimate_id=estimate_id,
            vessel=request.vessel,
            service_description=request.description,
            labor_items=labor_items,
            parts_items=parts_items,
            labor_subtotal=round(labor_subtotal, 2),
            parts_subtotal=round(parts_subtotal, 2),
            total_estimate=round(total_estimate, 2),
            estimate_range=estimate_range,
            confidence_score=round(confidence_score, 4),
            similar_jobs_count=len(similar_jobs),
            similar_jobs_summary=similar_jobs_summary,
            generated_at=datetime.utcnow(),
            status=EstimateStatus.DRAFT
        )
    
    def _retrieve_similar_jobs(self, request: ServiceRequest) -> List[SimilarJob]:
        """
        Retrieve similar historical jobs using RAG engine.
        
        Args:
            request: The service request
            
        Returns:
            List of similar jobs ordered by relevance
        """
        try:
            similar_jobs = self.rag_engine.retrieve_similar_jobs(
                service_description=request.description,
                vessel=request.vessel,
                top_k=10,
                service_category_filter=request.service_category.value if request.service_category else None
            )
            return similar_jobs
        except Exception as e:
            # Log error and return empty list (graceful degradation)
            print(f"Warning: RAG retrieval failed: {e}")
            return []
    
    def _get_parts_patterns(self, similar_jobs: List[SimilarJob]) -> List[dict]:
        """
        Get parts usage patterns from similar jobs.
        
        Args:
            similar_jobs: List of similar jobs
            
        Returns:
            List of parts patterns with usage counts
        """
        if not similar_jobs:
            return []
        
        work_order_ids = [job.work_order_id for job in similar_jobs]
        return self.rag_engine.get_parts_patterns(work_order_ids)
    
    def _build_labor_items(
        self,
        recommendation,
        similar_jobs: List[SimilarJob]
    ) -> List[EstimateLineItem]:
        """
        Build labor line items from recommendation.
        
        Args:
            recommendation: EstimateRecommendation from mock LLM
            similar_jobs: Similar jobs for reference text
            
        Returns:
            List of EstimateLineItem for labor
        """
        labor_items = []
        
        for labor_rec in recommendation.labor_recommendations:
            # Build source reference
            if similar_jobs:
                source_ref = f"Based on {len(similar_jobs)} similar jobs"
            else:
                source_ref = "Based on standard service times"
            
            labor_items.append(EstimateLineItem(
                line_type=LineType.LABOR,
                description=labor_rec.description,
                quantity=labor_rec.hours,
                unit="hours",
                unit_price=labor_rec.rate,
                total_price=labor_rec.total,
                confidence=labor_rec.confidence,
                source_reference=source_ref
            ))
        
        return labor_items
    
    def _build_parts_items(
        self,
        recommendation,
        vessel: Vessel,
        parts_patterns: List[dict]
    ) -> List[EstimateLineItem]:
        """
        Build parts line items from recommendation, validated against catalog.
        
        Args:
            recommendation: EstimateRecommendation from mock LLM
            vessel: Vessel for engine compatibility
            parts_patterns: Parts patterns from similar jobs
            
        Returns:
            List of EstimateLineItem for parts
        """
        parts_items = []
        used_part_numbers = set()
        
        # First, try to use parts from similar job patterns (validated)
        if parts_patterns:
            validated_parts = self.parts_catalog.validate_parts_from_similar_jobs(
                parts_patterns[:5],  # Top 5 most common parts
                vessel.engine_make
            )
            
            for part in validated_parts:
                if part['part_number'] not in used_part_numbers:
                    parts_items.append(EstimateLineItem(
                        line_type=LineType.PARTS,
                        description=part['description'],
                        quantity=round(part['quantity'], 1),
                        unit=part['unit'],
                        unit_price=part['unit_price'],
                        total_price=part['total_price'],
                        confidence=0.90,  # High confidence for validated parts
                        part_number=part['part_number'],
                        source_reference=f"Used in {part['usage_count']} similar jobs"
                    ))
                    used_part_numbers.add(part['part_number'])
        
        # Then, fill in from template recommendations
        for parts_rec in recommendation.parts_recommendations:
            # Find matching part in catalog
            catalog_part = self.parts_catalog.find_parts_for_service(
                category=parts_rec.category,
                part_type=parts_rec.part_type,
                engine_make=vessel.engine_make,
                quantity=int(parts_rec.quantity),
                unit=parts_rec.unit
            )
            
            if catalog_part and catalog_part['part_number'] not in used_part_numbers:
                confidence = 0.85 if parts_rec.is_required else 0.70
                
                parts_items.append(EstimateLineItem(
                    line_type=LineType.PARTS,
                    description=catalog_part['description'],
                    quantity=catalog_part['quantity'],
                    unit=catalog_part['unit'],
                    unit_price=catalog_part['unit_price'],
                    total_price=catalog_part['total_price'],
                    confidence=confidence,
                    part_number=catalog_part['part_number'],
                    source_reference="Recommended for this service"
                ))
                used_part_numbers.add(catalog_part['part_number'])
        
        return parts_items
    
    def _calculate_confidence(
        self,
        recommendation,
        similar_jobs: List[SimilarJob],
        vessel: Vessel
    ) -> float:
        """
        Calculate overall confidence score for the estimate.
        
        Combines:
        - RAG engine confidence (similar job count and match quality)
        - Mock LLM confidence (template match quality)
        
        Args:
            recommendation: EstimateRecommendation from mock LLM
            similar_jobs: Similar jobs from RAG
            vessel: Vessel for match scoring
            
        Returns:
            Overall confidence score (0-1)
        """
        # Get RAG-based confidence
        rag_confidence = self.rag_engine.calculate_confidence_score(
            similar_jobs,
            vessel
        )
        
        # Get LLM-based confidence
        llm_confidence = recommendation.labor_confidence
        template_confidence = recommendation.service_classification.confidence
        
        # Weighted combination
        # RAG confidence is weighted higher when we have good similar job coverage
        if len(similar_jobs) >= 5:
            # Good RAG coverage - weight it heavily
            combined = (
                0.4 * rag_confidence +
                0.35 * llm_confidence +
                0.25 * template_confidence
            )
        elif len(similar_jobs) >= 2:
            # Some RAG coverage
            combined = (
                0.3 * rag_confidence +
                0.4 * llm_confidence +
                0.3 * template_confidence
            )
        else:
            # Limited RAG coverage - rely more on template matching
            combined = (
                0.2 * rag_confidence +
                0.4 * llm_confidence +
                0.4 * template_confidence
            )
        
        return min(0.98, max(0.3, combined))


# Global singleton instance
_estimate_generator: Optional[EstimateGenerator] = None


def get_estimate_generator() -> EstimateGenerator:
    """Get the global estimate generator instance"""
    global _estimate_generator
    if _estimate_generator is None:
        _estimate_generator = EstimateGenerator()
    return _estimate_generator
