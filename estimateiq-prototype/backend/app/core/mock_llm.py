"""
EstimateIQ Mock LLM Service

Template-based estimate generation that simulates LLM behavior.
Provides consistent, demo-ready estimates without API costs.

This service:
1. Classifies service requests into categories and types
2. Matches requests to estimate templates
3. Generates labor and parts recommendations
4. Adjusts estimates based on vessel specifications
5. Calculates confidence scores

Easy to swap out for real Claude API in production.
"""

import json
import re
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

from app.core.config import settings
from app.models import Vessel, SimilarJob


@dataclass
class ServiceClassification:
    """Result of classifying a service request"""
    category: str
    service_type: str
    template: Dict[str, Any]
    keyword_matches: List[str]
    confidence: float


@dataclass
class LaborRecommendation:
    """A recommended labor line item"""
    description: str
    hours: float
    rate: float
    total: float
    confidence: float


@dataclass
class PartRecommendation:
    """A recommended parts line item"""
    category: str
    part_type: str
    quantity: float
    unit: str
    is_required: bool


@dataclass
class EstimateRecommendation:
    """Complete estimate recommendation from mock LLM"""
    service_classification: ServiceClassification
    labor_recommendations: List[LaborRecommendation]
    parts_recommendations: List[PartRecommendation]
    estimated_total_hours: float
    labor_confidence: float
    notes: Optional[str] = None


class MockLLMService:
    """
    Mock LLM service that generates estimates using templates.
    
    Simulates AI behavior by:
    - Pattern matching service descriptions to templates
    - Using historical data from similar jobs to refine estimates
    - Adjusting for vessel specifications
    - Generating realistic confidence scores
    """
    
    def __init__(self, templates_path: Optional[Path] = None):
        """
        Initialize the mock LLM service.
        
        Args:
            templates_path: Optional custom path to templates JSON.
                          Defaults to configured data directory.
        """
        self._templates_path = templates_path or (settings.data_dir / "estimate_templates.json")
        self._labor_rates_path = settings.data_dir / settings.labor_rates_file
        self._templates_cache: Optional[Dict] = None
        self._labor_rates_cache: Optional[Dict] = None
    
    def _load_templates(self) -> Dict:
        """Load and cache estimate templates"""
        if self._templates_cache is None:
            with open(self._templates_path, 'r') as f:
                self._templates_cache = json.load(f)
        return self._templates_cache
    
    def _load_labor_rates(self) -> Dict:
        """Load and cache labor rates"""
        if self._labor_rates_cache is None:
            with open(self._labor_rates_path, 'r') as f:
                self._labor_rates_cache = json.load(f)
        return self._labor_rates_cache
    
    def classify_service(
        self,
        description: str,
        service_category: Optional[str] = None
    ) -> ServiceClassification:
        """
        Classify a service request into a category and type.
        
        Uses keyword matching to find the best matching template.
        
        Args:
            description: The service description text
            service_category: Optional pre-specified category
            
        Returns:
            ServiceClassification with matched template and confidence
        """
        templates = self._load_templates()
        description_lower = description.lower()
        
        best_match = None
        best_score = 0
        best_matches = []
        
        # Search through all categories and service types
        categories_to_search = (
            [service_category] if service_category 
            else templates.get('service_templates', {}).keys()
        )
        
        for category in categories_to_search:
            category_templates = templates.get('service_templates', {}).get(category, {})
            
            for service_type, template in category_templates.items():
                keywords = template.get('keywords', [])
                matches = []
                
                for keyword in keywords:
                    if keyword.lower() in description_lower:
                        matches.append(keyword)
                
                # Score based on number and quality of matches
                score = len(matches)
                
                # Bonus for longer keyword matches (more specific)
                for match in matches:
                    score += len(match.split()) * 0.5
                
                if score > best_score:
                    best_score = score
                    best_match = (category, service_type, template)
                    best_matches = matches
        
        # If no match found, use default template
        if best_match is None:
            default = templates.get('default_template', {})
            # If service_category was specified, use it even without keyword match
            if service_category:
                return ServiceClassification(
                    category=service_category,
                    service_type='general',
                    template=default,
                    keyword_matches=[],
                    confidence=0.5  # Slightly higher than pure default
                )
            return ServiceClassification(
                category='general',
                service_type='general',
                template=default,
                keyword_matches=[],
                confidence=0.4
            )
        
        category, service_type, template = best_match
        
        # Calculate confidence based on match quality
        confidence = min(0.95, 0.5 + (best_score * 0.1))
        
        return ServiceClassification(
            category=category,
            service_type=service_type,
            template=template,
            keyword_matches=best_matches,
            confidence=confidence
        )
    
    def generate_estimate(
        self,
        service_description: str,
        vessel: Vessel,
        similar_jobs: List[SimilarJob],
        service_category: Optional[str] = None,
        region: str = "Northeast"
    ) -> EstimateRecommendation:
        """
        Generate a complete estimate recommendation.
        
        This is the main entry point for estimate generation.
        
        Args:
            service_description: The service request description
            vessel: Vessel specifications
            similar_jobs: Similar jobs from RAG engine
            service_category: Optional pre-specified category
            region: Geographic region for rate adjustments
            
        Returns:
            EstimateRecommendation with labor and parts suggestions
        """
        # Classify the service request
        classification = self.classify_service(
            service_description, 
            service_category
        )
        
        # Generate labor recommendations
        labor_recs = self._generate_labor_recommendations(
            classification=classification,
            vessel=vessel,
            similar_jobs=similar_jobs,
            region=region
        )
        
        # Generate parts recommendations
        parts_recs = self._generate_parts_recommendations(
            classification=classification,
            similar_jobs=similar_jobs
        )
        
        # Calculate totals
        total_hours = sum(rec.hours for rec in labor_recs)
        
        # Overall labor confidence
        if labor_recs:
            labor_confidence = sum(rec.confidence for rec in labor_recs) / len(labor_recs)
        else:
            labor_confidence = classification.confidence
        
        # Adjust confidence based on similar jobs
        if similar_jobs:
            similar_boost = min(0.1, len(similar_jobs) * 0.01)
            labor_confidence = min(0.98, labor_confidence + similar_boost)
        
        return EstimateRecommendation(
            service_classification=classification,
            labor_recommendations=labor_recs,
            parts_recommendations=parts_recs,
            estimated_total_hours=total_hours,
            labor_confidence=labor_confidence,
            notes=self._generate_notes(classification, similar_jobs)
        )
    
    def _generate_labor_recommendations(
        self,
        classification: ServiceClassification,
        vessel: Vessel,
        similar_jobs: List[SimilarJob],
        region: str
    ) -> List[LaborRecommendation]:
        """Generate labor line item recommendations"""
        labor_rates = self._load_labor_rates()
        template = classification.template
        
        # Get base labor rate for this category
        category_rate = labor_rates.get('rates_by_category', {}).get(
            classification.category,
            labor_rates.get('default_rate', 125.0)
        )
        
        # Apply regional multiplier
        region_multiplier = labor_rates.get('rates_by_region', {}).get(region, 1.0)
        adjusted_rate = category_rate * region_multiplier
        
        # Get LOA adjustment
        loa_adjustment = self._get_loa_adjustment(vessel.loa)
        labor_multiplier = loa_adjustment.get('labor_multiplier', 1.0)
        
        # Generate from template tasks
        recommendations = []
        labor_tasks = template.get('labor_tasks', [])
        
        # If we have similar jobs, use their labor hours for reference
        avg_similar_hours = None
        if similar_jobs:
            valid_hours = [j.total_labor_hours for j in similar_jobs if j.total_labor_hours > 0]
            if valid_hours:
                avg_similar_hours = sum(valid_hours) / len(valid_hours)
        
        for task in labor_tasks:
            base_hours = task.get('base_hours', 1.0)
            
            # Apply LOA multiplier
            adjusted_hours = base_hours * labor_multiplier
            
            # Also apply any template-specific LOA multiplier
            if 'loa_multiplier' in template:
                adjusted_hours += vessel.loa * template['loa_multiplier']
            
            # If similar jobs exist, blend with their average
            if avg_similar_hours and len(similar_jobs) >= 3:
                # Weight toward similar jobs when we have good data
                ratio = len(labor_tasks)  # Distribute similar hours across tasks
                adjusted_hours = (adjusted_hours * 0.4) + ((avg_similar_hours / ratio) * 0.6)
            
            # Round to nearest 0.25 hours
            adjusted_hours = round(adjusted_hours * 4) / 4
            adjusted_hours = max(0.25, adjusted_hours)  # Minimum 15 minutes
            
            # Format description
            description = task.get('description_template', task.get('task', 'Service'))
            description = description.format(
                engine_make=vessel.engine_make,
                engine_model=vessel.engine_model,
                vessel_loa=vessel.loa
            )
            
            # Calculate confidence
            confidence = classification.confidence
            if similar_jobs:
                # Higher confidence with more similar jobs
                confidence = min(0.95, confidence + (len(similar_jobs) * 0.02))
            
            recommendations.append(LaborRecommendation(
                description=description,
                hours=adjusted_hours,
                rate=round(adjusted_rate, 2),
                total=round(adjusted_hours * adjusted_rate, 2),
                confidence=round(confidence, 2)
            ))
        
        # If no template tasks, create a generic one
        if not recommendations:
            base_hours = template.get('base_labor_hours', 2.0) * labor_multiplier
            base_hours = round(base_hours * 4) / 4
            
            recommendations.append(LaborRecommendation(
                description=f"Service as requested - {vessel.engine_make}",
                hours=base_hours,
                rate=round(adjusted_rate, 2),
                total=round(base_hours * adjusted_rate, 2),
                confidence=round(classification.confidence * 0.8, 2)
            ))
        
        return recommendations
    
    def _generate_parts_recommendations(
        self,
        classification: ServiceClassification,
        similar_jobs: List[SimilarJob]
    ) -> List[PartRecommendation]:
        """Generate parts recommendations from template"""
        template = classification.template
        recommendations = []
        
        # Add required parts
        for part in template.get('required_parts', []):
            recommendations.append(PartRecommendation(
                category=part.get('category', 'General'),
                part_type=part.get('type', 'generic'),
                quantity=part.get('quantity', 1),
                unit=part.get('unit', 'each'),
                is_required=True
            ))
        
        # Add optional parts based on probability
        # (In a real LLM, this would be context-dependent)
        # For demo, we include optional parts if similar jobs suggest them
        similar_count = len(similar_jobs) if similar_jobs else 0
        
        for part in template.get('optional_parts', []):
            probability = part.get('probability', 0.5)
            
            # Include if we have good similar job coverage
            if similar_count >= 5 or probability > 0.4:
                recommendations.append(PartRecommendation(
                    category=part.get('category', 'General'),
                    part_type=part.get('type', 'generic'),
                    quantity=part.get('quantity', 1),
                    unit=part.get('unit', 'each'),
                    is_required=False
                ))
        
        return recommendations
    
    def _get_loa_adjustment(self, loa: float) -> Dict[str, float]:
        """Get LOA-based adjustment factors"""
        templates = self._load_templates()
        adjustments = templates.get('loa_adjustments', {})
        
        if loa < 20:
            return adjustments.get('under_20', {'labor_multiplier': 0.8, 'parts_multiplier': 0.9})
        elif loa < 25:
            return adjustments.get('20_25', {'labor_multiplier': 0.9, 'parts_multiplier': 0.95})
        elif loa < 30:
            return adjustments.get('25_30', {'labor_multiplier': 1.0, 'parts_multiplier': 1.0})
        elif loa < 35:
            return adjustments.get('30_35', {'labor_multiplier': 1.15, 'parts_multiplier': 1.1})
        elif loa < 40:
            return adjustments.get('35_40', {'labor_multiplier': 1.3, 'parts_multiplier': 1.2})
        else:
            return adjustments.get('over_40', {'labor_multiplier': 1.5, 'parts_multiplier': 1.3})
    
    def _generate_notes(
        self,
        classification: ServiceClassification,
        similar_jobs: List[SimilarJob]
    ) -> str:
        """Generate notes about the estimate"""
        notes_parts = []
        
        if classification.keyword_matches:
            notes_parts.append(
                f"Matched service type: {classification.service_type}"
            )
        
        if similar_jobs:
            notes_parts.append(
                f"Referenced {len(similar_jobs)} similar historical jobs"
            )
        
        if classification.confidence < 0.7:
            notes_parts.append(
                "Lower confidence estimate - recommend service writer review"
            )
        
        return "; ".join(notes_parts) if notes_parts else None
    
    def calculate_estimate_range(
        self,
        base_total: float,
        confidence: float,
        similar_jobs: List[SimilarJob]
    ) -> Tuple[float, float, float]:
        """
        Calculate low/expected/high estimate range.
        
        Args:
            base_total: The base estimate total
            confidence: Overall confidence score
            similar_jobs: Similar jobs for variance calculation
            
        Returns:
            Tuple of (low, expected, high) estimates
        """
        # Calculate variance from similar jobs
        if similar_jobs:
            invoices = [j.total_invoice for j in similar_jobs if j.total_invoice > 0]
            if len(invoices) >= 2:
                mean = sum(invoices) / len(invoices)
                variance = sum((x - mean) ** 2 for x in invoices) / len(invoices)
                std_dev = variance ** 0.5
                variance_ratio = std_dev / mean if mean > 0 else 0.2
                variance_ratio = min(0.3, variance_ratio)  # Cap at 30%
            else:
                variance_ratio = 0.15
        else:
            variance_ratio = 0.2
        
        # Adjust variance by confidence (lower confidence = wider range)
        confidence_adjustment = 1 + (1 - confidence) * 0.5
        variance_ratio *= confidence_adjustment
        
        low = round(base_total * (1 - variance_ratio), 2)
        expected = round(base_total, 2)
        high = round(base_total * (1 + variance_ratio * 1.5), 2)
        
        return low, expected, high


# Global singleton instance
_mock_llm_service: Optional[MockLLMService] = None


def get_mock_llm_service() -> MockLLMService:
    """Get the global mock LLM service instance"""
    global _mock_llm_service
    if _mock_llm_service is None:
        _mock_llm_service = MockLLMService()
    return _mock_llm_service
