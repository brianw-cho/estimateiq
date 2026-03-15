# EstimateIQ Phase 2 Implementation - Complete

## Summary

Phase 2 (RAG Engine) of the EstimateIQ prototype has been completed. This document provides context for the next agent to continue with Phase 3 implementation.

## What Was Built

### RAG Engine Components

**Location:** `estimateiq-prototype/backend/app/services/`

| File | Purpose |
|------|---------|
| `embedding_service.py` | Manages text embeddings and ChromaDB vector store |
| `rag_engine.py` | Retrieval logic, similarity scoring, confidence calculation |

### New API Endpoints

**Location:** `estimateiq-prototype/backend/app/api/routes/similar_jobs.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/similar-jobs` | GET | Find similar jobs by service description with optional filters |
| `/api/similar-jobs/with-vessel` | POST | Find similar jobs with full vessel context |
| `/api/similar-jobs/{work_order_id}` | GET | Get full work order details |
| `/api/similar-jobs/stats/labor-hours` | GET | Get labor statistics for similar jobs |
| `/api/similar-jobs/stats/parts-patterns` | GET | Get commonly used parts for similar jobs |

### Vector Store Setup Script

**Location:** `estimateiq-prototype/backend/scripts/build_vector_store.py`

Run with:
```bash
cd estimateiq-prototype/backend
source venv/bin/activate
python -m scripts.build_vector_store --reset --test
```

## Key Implementation Details

### Embedding Service

- Uses `sentence-transformers` with `all-MiniLM-L6-v2` model
- Creates combined text from service description, vessel type, engine make/model
- Stores embeddings in ChromaDB persistent collection

```python
def create_work_order_embedding_text(self, work_order: dict) -> str:
    """Combines key fields for embedding"""
    parts = [
        f"Service: {work_order.get('service_description', '')}",
        f"Vessel: {work_order.get('vessel_type', '')}",
        f"Length: {work_order.get('loa_range', '')} feet",
        f"Engine: {work_order.get('engine_make', '')} {work_order.get('engine_model', '')}",
        f"Category: {work_order.get('service_category', '')}",
    ]
    return " | ".join(parts)
```

### Similarity Scoring

ChromaDB returns L2 (Euclidean) distance. Converted to similarity using:
```python
similarity_score = 1 / (1 + distance)
```

Typical similarity scores:
- 0.45-0.55: Excellent match (same service type)
- 0.35-0.45: Good match (related services)
- <0.35: Weak match

### Confidence Calculation

Multi-factor confidence scoring (from design document):
```python
confidence = (
    0.3 * (min(similar_job_count, 20) / 20) +
    0.3 * avg_similarity_score +
    0.2 * (1 - labor_variance_normalized) +
    0.2 * vessel_match_score
)
```

Factors:
1. **Similar job count** (30%): More matches = higher confidence
2. **Average similarity** (30%): Better semantic match = higher confidence
3. **Labor variance** (20%): Lower variance = more consistent, higher confidence
4. **Vessel match** (20%): Matching engine make = higher confidence

### Vessel-Specific Boosting

When vessel context is provided, similarity scores are boosted:
- +0.05 for engine make match
- +0.05 for engine model match (additional)
- +0.03 for LOA within 5 feet (scaled by proximity)

## Dependencies Updated

```text
# requirements.txt changes
chromadb>=0.5.0  # Updated from 0.4.22 (numpy 2.x compatibility)
sentence-transformers>=2.3.1
pydantic-settings==2.1.0  # Added for config
```

**Important:** Use Python 3.12 for compatibility. Python 3.14 has issues with pydantic-core.

## How to Test Phase 2

### Start Backend

```bash
cd estimateiq-prototype/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Test Endpoints

```bash
# Find similar jobs
curl "http://localhost:8000/api/similar-jobs?description=oil+change&limit=5"

# With engine filter
curl "http://localhost:8000/api/similar-jobs?description=oil+change&engine_make=Volvo%20Penta"

# Labor statistics
curl "http://localhost:8000/api/similar-jobs/stats/labor-hours?description=winterization"

# Parts patterns
curl "http://localhost:8000/api/similar-jobs/stats/parts-patterns?description=oil+change"
```

### API Documentation

Visit http://localhost:8000/docs for interactive Swagger documentation.

## Phase 3 Tasks (Mock LLM & Estimate Generation)

Per the implementation plan, Phase 3 should implement:

### 1. Mock LLM Service

```python
# Location: backend/app/core/mock_llm.py

class MockLLMService:
    def __init__(self, templates, historical_patterns):
        self.templates = templates
        self.patterns = historical_patterns
    
    def generate_estimate(
        self,
        service_request: str,
        similar_jobs: List[SimilarJob],
        parts_catalog: List[Part]
    ) -> EstimateResponse:
        # 1. Classify service type
        # 2. Match to template
        # 3. Adjust based on vessel specs
        # 4. Generate labor and parts items
        pass
```

### 2. Estimate Templates

Create templates for each service category:
- `engine`: Oil change, tune-up, winterization
- `hull`: Cleaning, painting, repair
- `electrical`: Wiring, electronics, batteries
- `mechanical`: Steering, trim, hydraulics
- `outboard`: Impeller, lower unit, prop
- `inboard`: Transmission, shaft, exhaust
- `annual`: Spring commissioning, winterization
- `diagnostic`: Troubleshooting, inspection

### 3. Parts Catalog Integration

```python
# Location: backend/app/services/parts_catalog.py

class PartsCatalogService:
    def find_parts_for_service(
        self,
        service_category: str,
        engine_make: str,
        similar_parts: List[dict]  # From RAG engine
    ) -> List[Part]:
        # Match parts from catalog based on:
        # 1. Similar jobs parts patterns
        # 2. Engine compatibility
        # 3. Service category
        pass
```

### 4. Update Estimate Endpoint

Integrate RAG engine and mock LLM into the existing `/api/estimates` endpoint:

```python
@router.post("", response_model=Estimate)
async def generate_estimate(request: ServiceRequest) -> Estimate:
    # 1. Get similar jobs from RAG engine
    similar_jobs = rag_engine.retrieve_similar_jobs(
        service_description=request.description,
        vessel=request.vessel
    )
    
    # 2. Get parts patterns
    parts_patterns = rag_engine.get_parts_patterns(
        [job.work_order_id for job in similar_jobs]
    )
    
    # 3. Generate estimate using mock LLM
    estimate = mock_llm.generate_estimate(
        service_request=request.description,
        similar_jobs=similar_jobs,
        parts_catalog=parts_patterns
    )
    
    # 4. Calculate confidence from RAG results
    estimate.confidence_score = rag_engine.calculate_confidence_score(similar_jobs)
    estimate.similar_jobs_count = len(similar_jobs)
    estimate.similar_jobs_summary = rag_engine.get_similar_jobs_summary(similar_jobs)
    
    return estimate
```

## Files to Modify in Phase 3

| File | Changes Needed |
|------|----------------|
| `app/core/mock_llm.py` | Create new file with template-based generator |
| `app/services/parts_catalog.py` | Create new file for parts lookup |
| `app/api/routes/estimates.py` | Integrate RAG and mock LLM |
| `app/data/estimate_templates.json` | Create templates for each service type |

## Key Services Available for Phase 3

### From RAG Engine

```python
from app.services import get_rag_engine

rag = get_rag_engine()

# Get similar jobs
similar_jobs = rag.retrieve_similar_jobs(
    service_description="oil change",
    vessel=vessel,  # Optional Vessel object
    top_k=10
)

# Get confidence score
confidence = rag.calculate_confidence_score(similar_jobs, vessel)

# Get summary text
summary = rag.get_similar_jobs_summary(similar_jobs, vessel)

# Get labor statistics
stats = rag.get_labor_statistics(similar_jobs)
# Returns: {'min': 1.0, 'max': 2.5, 'mean': 1.5, 'median': 1.5}

# Get parts patterns
parts = rag.get_parts_patterns([job.work_order_id for job in similar_jobs])
# Returns list of commonly used parts with counts and avg prices

# Get full work order
wo = rag.get_full_work_order("WO-2024-0001")
```

### Available Data

The RAG engine has access to:
- 100 indexed work orders in ChromaDB
- Full work order details via JSON cache
- Parts catalog (300 items) at `app/data/parts_catalog.json`
- Labor rates at `app/data/labor_rates.json`

## Architecture Overview

```
                                 ┌──────────────────┐
                                 │   /api/estimates │
                                 └────────┬─────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           │                             │
                    ┌──────▼──────┐              ┌───────▼───────┐
                    │  RAG Engine │              │   Mock LLM    │
                    │  (Phase 2)  │              │   (Phase 3)   │
                    └──────┬──────┘              └───────┬───────┘
                           │                             │
              ┌────────────┴────────────┐        ┌──────▼──────┐
              │                         │        │  Templates  │
       ┌──────▼──────┐           ┌──────▼──────┐ │  (Phase 3)  │
       │  Embedding  │           │  ChromaDB   │ └─────────────┘
       │   Service   │           │ Vector Store│
       └──────┬──────┘           └──────┬──────┘
              │                         │
       ┌──────▼──────┐           ┌──────▼──────┐
       │  sentence-  │           │  100 Work   │
       │ transformers│           │   Orders    │
       └─────────────┘           └─────────────┘
```

## Test Results Summary

| Query | Top Result | Similarity |
|-------|------------|------------|
| "oil change" | Oil and filter change | 0.44 |
| "bottom paint and hull cleaning" | Hull cleaning and bottom paint | 0.54 |
| "winterization service" | Winterization | 0.47 |
| "lower unit service" | Lower unit service | 0.53 |
| "electrical troubleshooting" | Electrical troubleshooting | 0.42 |

---

*Phase 2 completed: March 2026*
