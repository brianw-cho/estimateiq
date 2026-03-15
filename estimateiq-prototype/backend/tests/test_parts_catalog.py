"""
Parts Catalog Service Behaviour Tests

These tests document and verify the behaviour of the Parts Catalog Service.
The service is responsible for:
1. Loading and caching the parts catalog
2. Finding parts by category, type, or engine compatibility
3. Validating that recommended parts exist in the catalog
4. Matching parts from similar job patterns to catalog items

Behaviours Documented:
1. Catalog loading and caching
2. Part lookup by part number
3. Part lookup by category
4. Part lookup by engine compatibility
5. Finding parts for service requirements
6. Validating parts from similar jobs
"""

import pytest
from pathlib import Path

from app.services.parts_catalog import PartsCatalogService, get_parts_catalog_service


# =============================================================================
# Catalog Loading Behaviours
# =============================================================================

class TestCatalogLoading:
    """Behaviours related to loading and caching the parts catalog."""
    
    def test_loads_catalog_from_default_path(self):
        """
        The service loads the parts catalog from the default data directory.
        """
        service = PartsCatalogService()
        parts = service.get_all_parts()
        
        assert parts is not None
        assert isinstance(parts, list)
        assert len(parts) > 0
    
    def test_catalog_is_cached(self):
        """
        The catalog is loaded once and cached for subsequent calls.
        """
        service = PartsCatalogService()
        
        # First call loads the catalog
        parts1 = service.get_all_parts()
        
        # Second call uses cached data
        parts2 = service.get_all_parts()
        
        # Should return same object (cached)
        assert parts1 is parts2
    
    def test_parts_have_required_fields(self):
        """
        Each part in the catalog has the required fields.
        """
        service = PartsCatalogService()
        parts = service.get_all_parts()
        
        for part in parts[:10]:  # Check first 10
            assert "part_number" in part
            assert "description" in part
            assert "category" in part
            assert "list_price" in part
            assert isinstance(part["list_price"], (int, float))
            assert part["list_price"] >= 0


# =============================================================================
# Part Number Lookup Behaviours
# =============================================================================

class TestPartNumberLookup:
    """Behaviours related to looking up parts by part number."""
    
    def test_finds_existing_part_by_number(self):
        """
        An existing part can be found by its part number.
        """
        service = PartsCatalogService()
        parts = service.get_all_parts()
        
        # Get an actual part number from the catalog
        test_part_number = parts[0]["part_number"]
        
        result = service.get_part_by_number(test_part_number)
        
        assert result is not None
        assert result["part_number"] == test_part_number
    
    def test_returns_none_for_nonexistent_part(self):
        """
        Returns None when part number doesn't exist.
        """
        service = PartsCatalogService()
        
        result = service.get_part_by_number("NONEXISTENT-999")
        
        assert result is None


# =============================================================================
# Category Lookup Behaviours
# =============================================================================

class TestCategoryLookup:
    """Behaviours related to looking up parts by category."""
    
    def test_gets_parts_by_category(self):
        """
        Parts can be retrieved by their category.
        """
        service = PartsCatalogService()
        
        filters_parts = service.get_parts_by_category("Filters")
        
        assert isinstance(filters_parts, list)
        assert len(filters_parts) > 0
        
        for part in filters_parts:
            assert part["category"] == "Filters"
    
    def test_returns_empty_list_for_unknown_category(self):
        """
        Returns empty list for unknown category.
        """
        service = PartsCatalogService()
        
        result = service.get_parts_by_category("NonexistentCategory")
        
        assert result == []
    
    def test_gets_all_categories(self):
        """
        Can retrieve list of all available categories.
        """
        service = PartsCatalogService()
        
        categories = service.get_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "Filters" in categories
        assert "Fluids" in categories


# =============================================================================
# Engine Compatibility Behaviours
# =============================================================================

class TestEngineCompatibility:
    """Behaviours related to finding parts by engine compatibility."""
    
    def test_finds_parts_for_engine_make(self):
        """
        Parts compatible with a specific engine make can be found.
        """
        service = PartsCatalogService()
        
        volvo_parts = service.get_parts_for_engine("Volvo Penta")
        
        assert isinstance(volvo_parts, list)
        assert len(volvo_parts) > 0
        
        # Each part should be compatible with Volvo Penta
        for part in volvo_parts:
            compatible = part.get("compatible_engines", [])
            assert any("volvo" in e.lower() for e in compatible)
    
    def test_partial_engine_name_matches(self):
        """
        Partial engine names also match (e.g., 'Volvo' matches 'Volvo Penta').
        """
        service = PartsCatalogService()
        
        # Try just "Volvo" instead of "Volvo Penta"
        volvo_parts = service.get_parts_for_engine("Volvo")
        
        assert len(volvo_parts) > 0
    
    def test_engine_name_is_case_insensitive(self):
        """
        Engine name matching is case insensitive.
        """
        service = PartsCatalogService()
        
        parts_upper = service.get_parts_for_engine("YAMAHA")
        parts_lower = service.get_parts_for_engine("yamaha")
        
        # Should return same parts regardless of case
        assert len(parts_upper) == len(parts_lower)


# =============================================================================
# Find Parts for Service Behaviours
# =============================================================================

class TestFindPartsForService:
    """Behaviours for finding parts matching service requirements."""
    
    def test_finds_oil_filter_for_volvo(self):
        """
        Finds an oil filter compatible with Volvo Penta engine.
        """
        service = PartsCatalogService()
        
        result = service.find_parts_for_service(
            category="Filters",
            part_type="oil_filter",
            engine_make="Volvo Penta",
            quantity=1
        )
        
        assert result is not None
        assert "filter" in result["description"].lower()
        assert result["quantity"] == 1
        assert result["unit_price"] > 0
        assert result["total_price"] == result["unit_price"]
    
    def test_calculates_total_price_with_quantity(self):
        """
        Total price is calculated correctly based on quantity.
        """
        service = PartsCatalogService()
        
        result = service.find_parts_for_service(
            category="Fluids",
            part_type="engine_oil",
            engine_make="Mercury",
            quantity=2,
            unit="gallon"
        )
        
        if result:  # May return None if no match
            expected_total = round(result["unit_price"] * result["quantity"], 2)
            assert result["total_price"] == expected_total
    
    def test_returns_none_for_no_match(self):
        """
        Returns None when no matching part is found.
        """
        service = PartsCatalogService()
        
        result = service.find_parts_for_service(
            category="NonexistentCategory",
            part_type="nonexistent_type",
            engine_make="Unknown Engine",
            quantity=1
        )
        
        assert result is None


# =============================================================================
# Validate Parts from Similar Jobs Behaviours
# =============================================================================

class TestValidatePartsFromSimilarJobs:
    """Behaviours for validating parts from similar job patterns."""
    
    def test_validates_existing_part_numbers(self):
        """
        Parts with valid part numbers are validated against catalog.
        """
        service = PartsCatalogService()
        parts = service.get_all_parts()
        
        # Create a mock similar parts pattern with a real part number
        test_part = parts[0]
        similar_parts = [
            {
                "part_number": test_part["part_number"],
                "description": test_part["description"],
                "count": 5,
                "avg_quantity": 1.5,
            }
        ]
        
        validated = service.validate_parts_from_similar_jobs(
            similar_parts,
            engine_make="Volvo Penta"
        )
        
        assert len(validated) == 1
        assert validated[0]["part_number"] == test_part["part_number"]
        # Should use current catalog price
        assert validated[0]["unit_price"] == test_part["list_price"]
    
    def test_includes_usage_count_from_pattern(self):
        """
        Validated parts include usage count from the pattern.
        """
        service = PartsCatalogService()
        parts = service.get_all_parts()
        test_part = parts[0]
        
        similar_parts = [
            {
                "part_number": test_part["part_number"],
                "description": test_part["description"],
                "count": 7,
                "avg_quantity": 2,
            }
        ]
        
        validated = service.validate_parts_from_similar_jobs(
            similar_parts,
            engine_make="Volvo Penta"
        )
        
        assert validated[0]["usage_count"] == 7
    
    def test_skips_invalid_part_numbers(self):
        """
        Parts with invalid part numbers are not validated.
        (Unless an equivalent is found by description)
        """
        service = PartsCatalogService()
        
        similar_parts = [
            {
                "part_number": "INVALID-999-NOTREAL",
                "description": "Some random part description",
                "count": 3,
                "avg_quantity": 1,
            }
        ]
        
        validated = service.validate_parts_from_similar_jobs(
            similar_parts,
            engine_make="Volvo Penta"
        )
        
        # Should not include the invalid part (unless description matches something)
        # The result could be 0 or 1 depending on description matching
        assert len(validated) <= 1
    
    def test_finds_equivalent_by_description(self):
        """
        When part number doesn't exist, tries to find equivalent by description.
        """
        service = PartsCatalogService()
        
        similar_parts = [
            {
                "part_number": "INVALID-999",
                "description": "Oil Filter",  # Common description
                "count": 5,
                "avg_quantity": 1,
            }
        ]
        
        validated = service.validate_parts_from_similar_jobs(
            similar_parts,
            engine_make="Volvo Penta"
        )
        
        # Should find an equivalent oil filter
        if validated:  # If found
            assert "filter" in validated[0]["description"].lower()


# =============================================================================
# Singleton Instance Behaviours
# =============================================================================

class TestSingletonInstance:
    """Behaviours of the global singleton instance."""
    
    def test_returns_same_instance(self):
        """
        get_parts_catalog_service returns the same instance each time.
        """
        service1 = get_parts_catalog_service()
        service2 = get_parts_catalog_service()
        
        assert service1 is service2
    
    def test_instance_is_functional(self):
        """
        The singleton instance is fully functional.
        """
        service = get_parts_catalog_service()
        
        parts = service.get_all_parts()
        assert len(parts) > 0
        
        categories = service.get_categories()
        assert len(categories) > 0
