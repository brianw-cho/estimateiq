"""
EstimateIQ Parts Catalog Service

Provides part lookup and recommendation functionality based on:
- Service category and type
- Engine compatibility
- Historical usage patterns from similar jobs

All parts suggestions are grounded in the parts catalog - no hallucinated parts.
"""

import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.core.config import settings


class PartsCatalogService:
    """
    Service for looking up parts from the catalog.
    
    Key responsibilities:
    1. Load and cache the parts catalog
    2. Find parts by category, type, or engine compatibility
    3. Validate that recommended parts exist in the catalog
    4. Match parts from similar job patterns to catalog items
    """
    
    def __init__(self, catalog_path: Optional[Path] = None):
        """
        Initialize the parts catalog service.
        
        Args:
            catalog_path: Optional custom path to parts catalog JSON.
                         Defaults to configured data directory.
        """
        self._catalog_path = catalog_path or (settings.data_dir / settings.parts_catalog_file)
        self._catalog_cache: Optional[List[dict]] = None
        self._by_category: Optional[Dict[str, List[dict]]] = None
        self._by_engine: Optional[Dict[str, List[dict]]] = None
        self._by_part_number: Optional[Dict[str, dict]] = None
    
    def _load_catalog(self) -> List[dict]:
        """Load and cache the parts catalog"""
        if self._catalog_cache is None:
            with open(self._catalog_path, 'r') as f:
                self._catalog_cache = json.load(f)
            self._build_indexes()
        return self._catalog_cache
    
    def _build_indexes(self) -> None:
        """Build lookup indexes for fast access"""
        self._by_category = {}
        self._by_engine = {}
        self._by_part_number = {}
        
        for part in self._catalog_cache:
            # Index by category
            category = part.get('category', 'Unknown')
            if category not in self._by_category:
                self._by_category[category] = []
            self._by_category[category].append(part)
            
            # Index by compatible engines
            for engine in part.get('compatible_engines', []):
                engine_lower = engine.lower()
                if engine_lower not in self._by_engine:
                    self._by_engine[engine_lower] = []
                self._by_engine[engine_lower].append(part)
            
            # Index by part number
            self._by_part_number[part['part_number']] = part
    
    def get_all_parts(self) -> List[dict]:
        """Get all parts in the catalog"""
        return self._load_catalog()
    
    def get_part_by_number(self, part_number: str) -> Optional[dict]:
        """
        Look up a specific part by its part number.
        
        Args:
            part_number: The part number to look up
            
        Returns:
            Part dictionary or None if not found
        """
        self._load_catalog()
        return self._by_part_number.get(part_number)
    
    def get_parts_by_category(self, category: str) -> List[dict]:
        """
        Get all parts in a given category.
        
        Args:
            category: Category name (e.g., "Filters", "Fluids")
            
        Returns:
            List of parts in that category
        """
        self._load_catalog()
        return self._by_category.get(category, [])
    
    def get_parts_for_engine(self, engine_make: str) -> List[dict]:
        """
        Get all parts compatible with a given engine make.
        
        Args:
            engine_make: Engine manufacturer (e.g., "Volvo Penta", "Yamaha")
            
        Returns:
            List of compatible parts
        """
        self._load_catalog()
        engine_lower = engine_make.lower()
        
        # Try exact match first
        if engine_lower in self._by_engine:
            return self._by_engine[engine_lower]
        
        # Try partial match (e.g., "Volvo" matches "Volvo Penta")
        matching_parts = []
        for engine_key, parts in self._by_engine.items():
            if engine_lower in engine_key or engine_key in engine_lower:
                matching_parts.extend(parts)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_parts = []
        for part in matching_parts:
            if part['part_number'] not in seen:
                seen.add(part['part_number'])
                unique_parts.append(part)
        
        return unique_parts
    
    def find_parts_for_service(
        self,
        category: str,
        part_type: str,
        engine_make: str,
        quantity: int = 1,
        unit: str = "each"
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best matching part for a service requirement.
        
        Args:
            category: Part category (e.g., "Filters")
            part_type: Type of part (e.g., "oil_filter", "fuel_filter")
            engine_make: Engine manufacturer for compatibility
            quantity: Quantity needed
            unit: Unit of measure
            
        Returns:
            Part recommendation with quantity and pricing, or None if no match
        """
        self._load_catalog()
        
        # Get parts in the category
        category_parts = self.get_parts_by_category(category)
        if not category_parts:
            return None
        
        # Filter by engine compatibility
        engine_compatible = []
        engine_lower = engine_make.lower()
        
        for part in category_parts:
            compatible_engines = [e.lower() for e in part.get('compatible_engines', [])]
            if any(engine_lower in e or e in engine_lower for e in compatible_engines):
                engine_compatible.append(part)
        
        # If no engine-specific parts, use universal parts
        if not engine_compatible:
            engine_compatible = [
                p for p in category_parts 
                if 'Universal' in p.get('compatible_engines', []) or 
                   'All' in p.get('compatible_engines', []) or
                   len(p.get('compatible_engines', [])) == 0
            ]
        
        # Further filter by part type if specified
        if part_type and engine_compatible:
            type_matches = self._filter_by_type(engine_compatible, part_type)
            if type_matches:
                engine_compatible = type_matches
        
        if not engine_compatible:
            # Fall back to any part in the category
            engine_compatible = category_parts[:1] if category_parts else []
        
        if not engine_compatible:
            return None
        
        # Select the best match (first one after filtering)
        selected_part = engine_compatible[0]
        
        return {
            'part_number': selected_part['part_number'],
            'description': selected_part['description'],
            'category': selected_part['category'],
            'quantity': quantity,
            'unit': unit if unit else selected_part.get('unit', 'each'),
            'unit_price': selected_part['list_price'],
            'total_price': round(selected_part['list_price'] * quantity, 2),
        }
    
    def _filter_by_type(self, parts: List[dict], part_type: str) -> List[dict]:
        """
        Filter parts by type based on description keywords.
        
        Args:
            parts: List of parts to filter
            part_type: Type identifier (e.g., "oil_filter", "spark_plugs")
            
        Returns:
            Filtered list of parts matching the type
        """
        # Convert part_type to search terms
        type_terms = part_type.replace('_', ' ').lower().split()
        
        matches = []
        for part in parts:
            description_lower = part['description'].lower()
            if all(term in description_lower for term in type_terms):
                matches.append(part)
        
        return matches
    
    def validate_parts_from_similar_jobs(
        self,
        similar_parts: List[Dict[str, Any]],
        engine_make: str
    ) -> List[Dict[str, Any]]:
        """
        Validate and enrich parts from similar job patterns.
        
        Takes parts patterns from RAG engine and validates them against
        the catalog, ensuring we only recommend real parts.
        
        Args:
            similar_parts: Parts patterns from similar jobs
            engine_make: Engine make for compatibility filtering
            
        Returns:
            List of validated parts with current pricing
        """
        self._load_catalog()
        validated = []
        
        for pattern in similar_parts:
            part_number = pattern.get('part_number', '')
            
            # First try exact part number lookup
            catalog_part = self.get_part_by_number(part_number)
            
            if catalog_part:
                # Part exists, use current catalog pricing
                validated.append({
                    'part_number': catalog_part['part_number'],
                    'description': catalog_part['description'],
                    'category': catalog_part['category'],
                    'quantity': pattern.get('avg_quantity', 1),
                    'unit': catalog_part.get('unit', 'each'),
                    'unit_price': catalog_part['list_price'],
                    'total_price': round(
                        catalog_part['list_price'] * pattern.get('avg_quantity', 1), 2
                    ),
                    'usage_count': pattern.get('count', 1),
                })
            else:
                # Part number not found, try to find equivalent by description
                description = pattern.get('description', '')
                if description:
                    equivalent = self._find_equivalent_part(
                        description, engine_make
                    )
                    if equivalent:
                        validated.append({
                            'part_number': equivalent['part_number'],
                            'description': equivalent['description'],
                            'category': equivalent['category'],
                            'quantity': pattern.get('avg_quantity', 1),
                            'unit': equivalent.get('unit', 'each'),
                            'unit_price': equivalent['list_price'],
                            'total_price': round(
                                equivalent['list_price'] * pattern.get('avg_quantity', 1), 2
                            ),
                            'usage_count': pattern.get('count', 1),
                        })
        
        return validated
    
    def _find_equivalent_part(
        self,
        description: str,
        engine_make: str
    ) -> Optional[dict]:
        """
        Find an equivalent part based on description matching.
        
        Args:
            description: Part description to match
            engine_make: Engine make for compatibility
            
        Returns:
            Matching part or None
        """
        self._load_catalog()
        
        # Extract key terms from description
        desc_lower = description.lower()
        
        # Common part type keywords
        part_types = {
            'oil filter': ('Filters', 'oil'),
            'fuel filter': ('Filters', 'fuel'),
            'air filter': ('Filters', 'air'),
            'spark plug': ('Ignition', 'spark'),
            'impeller': ('Impellers', 'impeller'),
            'zinc': ('Zincs/Anodes', 'zinc'),
            'anode': ('Zincs/Anodes', 'anode'),
            'antifreeze': ('Fluids', 'antifreeze'),
            'coolant': ('Fluids', 'coolant'),
            'engine oil': ('Fluids', 'oil'),
            'gear lube': ('Fluids', 'gear'),
            'battery': ('Electrical', 'battery'),
        }
        
        # Try to match description to a part type
        for key, (category, search_term) in part_types.items():
            if key in desc_lower:
                parts = self.get_parts_by_category(category)
                engine_lower = engine_make.lower()
                
                # Find engine-compatible part
                for part in parts:
                    compatible = part.get('compatible_engines', [])
                    if any(engine_lower in e.lower() for e in compatible):
                        if search_term in part['description'].lower():
                            return part
                
                # Fall back to first matching part
                for part in parts:
                    if search_term in part['description'].lower():
                        return part
        
        return None
    
    def get_categories(self) -> List[str]:
        """Get all unique part categories"""
        self._load_catalog()
        return list(self._by_category.keys())
    
    def get_supported_engines(self) -> List[str]:
        """Get all supported engine makes"""
        self._load_catalog()
        return list(self._by_engine.keys())


# Global singleton instance
_parts_catalog_service: Optional[PartsCatalogService] = None


def get_parts_catalog_service() -> PartsCatalogService:
    """Get the global parts catalog service instance"""
    global _parts_catalog_service
    if _parts_catalog_service is None:
        _parts_catalog_service = PartsCatalogService()
    return _parts_catalog_service
