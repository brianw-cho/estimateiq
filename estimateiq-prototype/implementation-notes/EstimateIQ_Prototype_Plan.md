# EstimateIQ Prototype Implementation Plan

## Overview

This document outlines the implementation plan for building a functional prototype of **EstimateIQ**, an AI-powered service estimate generator for DockMaster's marine service operations.

**Objective:** Build a working prototype that demonstrates the core value proposition - transforming a 15-30 minute manual estimate process into a 5-minute AI-assisted workflow.

**Prototype Timeline:** 3-5 days for functional demonstration

**Target Audience:** Internal Valsoft stakeholders (executives, product managers)

**LLM Strategy:** Mock responses for prototype (easy to swap in real Claude API later)

---

## Table of Contents

1. [Prototype Scope](#prototype-scope)
2. [Architecture Design](#architecture-design)
3. [Technology Stack](#technology-stack)
4. [Data Model](#data-model)
5. [Component Breakdown](#component-breakdown)
6. [Implementation Phases](#implementation-phases)
7. [Design Decisions & Rationale](#design-decisions--rationale)
8. [Mock Data Strategy](#mock-data-strategy)
9. [Testing Strategy](#testing-strategy)
10. [Future Production Considerations](#future-production-considerations)

---

## Prototype Scope

### In Scope (MVP Features)

| Feature | Description | Priority |
|---------|-------------|----------|
| Vessel Input | Accept vessel specs (LOA, engine make/model, year) | P0 |
| Service Request Input | Free text description of service needed | P0 |
| AI Estimate Generation | Generate labor tasks with hour estimates | P0 |
| Parts Recommendations | Suggest parts with quantities | P0 |
| Confidence Scoring | Display confidence level for recommendations | P1 |
| Range Presentation | Show low/expected/high estimates | P1 |
| Similar Jobs Reference | Display "Based on X similar jobs..." | P1 |
| Human Review Interface | Allow editing before finalizing | P1 |

### Out of Scope (Production Features)

| Feature | Reason for Exclusion |
|---------|---------------------|
| Real PartSmart API Integration | Requires API access; will use mock pricing |
| Multi-tenant data isolation | Prototype is single-tenant demo |
| Real DockMaster DB connection | Will use synthetic training data |
| Authentication/Authorization | Not needed for prototype demo |
| Billing infrastructure | Not needed for prototype |
| Production-grade security | Focus on functionality first |
| Real Claude API | Using mock responses for cost efficiency |

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EstimateIQ Prototype                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐                                                         │
│  │   Frontend     │                                                         │
│  │   (Next.js)    │                                                         │
│  │                │                                                         │
│  │  - Vessel Form │                                                         │
│  │  - Service Req │                                                         │
│  │  - Estimate    │                                                         │
│  │    Display     │                                                         │
│  │  - Edit/Review │                                                         │
│  └───────┬────────┘                                                         │
│          │                                                                   │
│          │ REST API                                                          │
│          ▼                                                                   │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐            │
│  │   Backend API  │───▶│  RAG Engine    │───▶│  Mock LLM      │            │
│  │   (Python/     │    │                │    │  Service       │            │
│  │    FastAPI)    │    │  - Embedding   │    │                │            │
│  │                │    │  - Retrieval   │    │  - Template    │            │
│  │  - Endpoints   │    │  - Context     │    │    Generation  │            │
│  │  - Validation  │    │    Building    │    │  - Pattern     │            │
│  └───────┬────────┘    └───────┬────────┘    │    Matching    │            │
│          │                     │             └────────────────┘            │
│          ▼                     ▼                                            │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐            │
│  │  Mock Parts    │    │  Vector Store  │    │  Work Order    │            │
│  │  Catalog       │    │  (ChromaDB)    │    │  Database      │            │
│  │  (JSON)        │    │                │    │  (SQLite/JSON) │            │
│  └────────────────┘    └────────────────┘    └────────────────┘            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Frontend captures vessel specs + service description
2. **API Request** → Backend receives and validates input
3. **Embedding** → Service description embedded into vector representation
4. **Retrieval** → Similar historical work orders retrieved from vector store
5. **Context Building** → Retrieved jobs + vessel specs + parts catalog assembled
6. **Mock Generation** → Template-based system generates structured estimate
7. **Response** → Formatted estimate returned to frontend for display/editing

---

## Technology Stack

### Frontend

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | **Next.js 14** (App Router) | Modern React framework with SSR, good DX |
| Styling | **Tailwind CSS** | Rapid UI development, consistent design |
| UI Components | **shadcn/ui** | High-quality, accessible components |
| State Management | **React Hook Form** | Form handling for vessel/service inputs |
| HTTP Client | **fetch** (native) | Simple, no extra dependencies |

### Backend

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | **FastAPI** (Python) | Fast, modern, great for AI/ML integration |
| Vector Store | **ChromaDB** | Easy local setup, good for prototyping |
| Embeddings | **sentence-transformers** | Local embeddings, no API needed |
| Mock LLM | **Template-based generator** | No API costs, consistent demos |
| Database | **SQLite** + **JSON files** | Simple, no infrastructure needed |
| Validation | **Pydantic** | Type-safe request/response handling |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Poetry** or **pip** | Python dependency management |
| **pnpm** | JavaScript dependency management |
| **Docker** (optional) | Containerized deployment |

---

## Data Model

### Core Entities

#### Vessel

```python
class Vessel(BaseModel):
    vessel_id: Optional[str] = None
    name: Optional[str] = None
    loa: float  # Length Overall in feet
    beam: Optional[float] = None
    year: int
    engine_make: str
    engine_model: str
    engine_year: Optional[int] = None
    hull_type: Optional[str] = None  # fiberglass, aluminum, wood, steel
    propulsion_type: Optional[str] = None  # inboard, outboard, sterndrive, jet
```

#### ServiceRequest

```python
class ServiceRequest(BaseModel):
    vessel: Vessel
    description: str  # Free text service request
    service_category: Optional[str] = None  # engine, hull, electrical, etc.
    urgency: Optional[str] = "routine"  # routine, priority, emergency
    region: Optional[str] = "Northeast"  # for regional pricing patterns
```

#### EstimateLineItem

```python
class EstimateLineItem(BaseModel):
    line_type: str  # "labor" or "parts"
    description: str
    quantity: float
    unit: str  # "hours" for labor, "each"/"gallon"/etc. for parts
    unit_price: float
    total_price: float
    confidence: float  # 0.0 - 1.0
    source_reference: Optional[str] = None  # "Based on X similar jobs..."
```

#### Estimate

```python
class Estimate(BaseModel):
    estimate_id: str
    vessel: Vessel
    service_description: str
    labor_items: List[EstimateLineItem]
    parts_items: List[EstimateLineItem]
    labor_subtotal: float
    parts_subtotal: float
    total_estimate: float
    estimate_range: EstimateRange  # low/expected/high
    confidence_score: float
    similar_jobs_count: int
    similar_jobs_summary: str
    generated_at: datetime
    status: str  # "draft", "reviewed", "approved", "sent"
```

#### HistoricalWorkOrder (for RAG)

```python
class HistoricalWorkOrder(BaseModel):
    work_order_id: str
    vessel_type: str
    loa_range: str  # "20-25", "25-30", etc.
    engine_make: str
    engine_model: str
    service_category: str
    service_description: str
    labor_items: List[LaborItem]
    parts_used: List[PartItem]
    total_labor_hours: float
    total_parts_cost: float
    total_invoice: float
    completion_date: str
    region: str
    season: str  # spring, summer, fall, winter
```

---

## Component Breakdown

### Frontend Components

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                    # Landing/home page
│   │   ├── estimate/
│   │   │   ├── new/
│   │   │   │   └── page.tsx           # New estimate form
│   │   │   └── [id]/
│   │   │       └── page.tsx           # View/edit estimate
│   │   └── layout.tsx                  # Root layout
│   ├── components/
│   │   ├── estimate/
│   │   │   ├── VesselForm.tsx         # Vessel input form
│   │   │   ├── ServiceRequestForm.tsx # Service description input
│   │   │   ├── EstimateDisplay.tsx    # Generated estimate view
│   │   │   ├── LineItemEditor.tsx     # Edit individual line items
│   │   │   ├── ConfidenceIndicator.tsx # Visual confidence score
│   │   │   └── SimilarJobsRef.tsx     # "Based on X jobs" display
│   │   └── ui/                         # shadcn components
│   ├── lib/
│   │   ├── api.ts                      # API client functions
│   │   └── types.ts                    # TypeScript interfaces
│   └── styles/
│       └── globals.css                 # Tailwind + custom styles
├── package.json
└── tailwind.config.js
```

### Backend Components

```
backend/
├── app/
│   ├── main.py                     # FastAPI app entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── estimates.py       # Estimate generation endpoints
│   │   │   └── vessels.py         # Vessel lookup endpoints
│   │   └── deps.py                # Dependency injection
│   ├── core/
│   │   ├── config.py              # Configuration settings
│   │   └── mock_llm.py            # Mock LLM response generator
│   ├── services/
│   │   ├── estimate_generator.py  # Main estimation logic
│   │   ├── rag_engine.py          # RAG retrieval logic
│   │   ├── embedding_service.py   # Text embedding
│   │   └── parts_catalog.py       # Parts lookup (mock)
│   ├── models/
│   │   ├── schemas.py             # Pydantic models
│   │   └── database.py            # SQLite models
│   └── data/
│       ├── work_orders.json       # Synthetic work order data
│       ├── parts_catalog.json     # Mock parts catalog
│       └── labor_rates.json       # Standard labor rates
├── scripts/
│   ├── seed_data.py               # Generate synthetic data
│   └── build_vector_store.py      # Initialize ChromaDB
├── tests/
│   └── test_estimate_generator.py
├── pyproject.toml
└── requirements.txt
```

### Key Backend Services

#### 1. RAG Engine (`rag_engine.py`)

Responsibilities:
- Embed incoming service requests using sentence-transformers
- Query vector store for similar historical work orders
- Return top-k most relevant jobs with similarity scores

```python
class RAGEngine:
    def __init__(self, vector_store, embedding_service):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def retrieve_similar_jobs(
        self, 
        service_description: str,
        vessel: Vessel,
        top_k: int = 10
    ) -> List[SimilarJob]:
        # 1. Embed service description
        # 2. Query vector store with filters (vessel type, engine)
        # 3. Return ranked results with similarity scores
        pass
```

#### 2. Estimate Generator (`estimate_generator.py`)

Responsibilities:
- Orchestrate the full estimate generation flow
- Build context from retrieved jobs
- Generate estimate using mock LLM or templates
- Calculate confidence scores

```python
class EstimateGenerator:
    def __init__(self, rag_engine, mock_llm, parts_catalog):
        self.rag_engine = rag_engine
        self.mock_llm = mock_llm
        self.parts_catalog = parts_catalog
    
    def generate_estimate(self, request: ServiceRequest) -> Estimate:
        # 1. Retrieve similar jobs
        # 2. Build context with parts catalog
        # 3. Generate estimate via mock LLM
        # 4. Validate parts against catalog
        # 5. Calculate confidence scores
        # 6. Return structured estimate
        pass
```

#### 3. Mock LLM Service (`mock_llm.py`)

Responsibilities:
- Pattern-match service requests to templates
- Generate realistic estimates based on historical data patterns
- Provide consistent results for demo scenarios

```python
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

---

## Implementation Phases

### Phase 1: Foundation (Day 1)

**Tasks:**
1. Set up project structure (frontend + backend)
2. Configure development environment
3. Create data models (Pydantic schemas)
4. Generate synthetic work order data (100 records)
5. Create mock parts catalog (300 common marine parts)
6. Set up basic FastAPI server
7. Set up basic Next.js app

**Deliverables:**
- Project skeleton with both frontend and backend
- Synthetic data files ready for use
- Basic FastAPI server running on port 8000
- Basic Next.js app running on port 3000

### Phase 2: RAG Engine (Day 2)

**Tasks:**
1. Set up ChromaDB vector store
2. Implement embedding service using sentence-transformers
3. Index synthetic work orders
4. Build retrieval logic with filtering by vessel/engine
5. Test retrieval quality
6. Create `/api/similar-jobs` endpoint

**Deliverables:**
- Working vector store with indexed work orders
- Retrieval endpoint returning similar jobs
- Basic similarity search working

### Phase 3: Mock LLM & Estimate Generation (Day 2-3)

**Tasks:**
1. Design estimate templates for common service types
2. Implement pattern matching for service classification
3. Build mock estimate generation logic
4. Implement confidence scoring algorithm
5. Add parts catalog validation
6. Create `/api/estimates` endpoint

**Deliverables:**
- Working estimate generation endpoint
- Structured JSON estimates returned
- Confidence scores calculated
- Similar jobs count and summary included

### Phase 4: Frontend UI (Day 3-4)

**Tasks:**
1. Install and configure shadcn/ui components
2. Build vessel input form with validation
3. Build service request form
4. Create estimate display component
5. Implement line item editing
6. Add confidence visualization (progress bars/badges)
7. Add estimate range display (low/expected/high)
8. Style with professional marine theme (blues, clean typography)

**Deliverables:**
- Complete user flow from input to estimate
- Editable estimate interface
- Professional-looking UI suitable for stakeholder demo

### Phase 5: Polish & Demo (Day 4-5)

**Tasks:**
1. Add loading states and error handling
2. Add "similar jobs" reference display
3. Create 5 demo scenarios with scripted inputs
4. Test end-to-end flows
5. Write README with setup instructions
6. Prepare demo script for stakeholders

**Deliverables:**
- Polished, demo-ready prototype
- 5 demo scenarios prepared
- README with setup instructions
- Demo script document

---

## Design Decisions & Rationale

### Decision 1: RAG vs. Fine-Tuning

**Decision:** Use RAG (Retrieval-Augmented Generation) architecture

**Rationale:**
- **Faster iteration:** No training required; can update data and see changes immediately
- **Transparency:** Can show "based on X similar jobs" which builds trust
- **Cost:** No training costs; works with mock LLM for prototype
- **Data efficiency:** Works well with limited training data
- **Explainability:** Retrieved examples provide justification for recommendations
- **Production path:** Same architecture works with real Claude API

### Decision 2: ChromaDB for Vector Store

**Decision:** Use ChromaDB over alternatives (Pinecone, Weaviate, pgvector)

**Rationale:**
- **Zero infrastructure:** Runs locally, no cloud setup or API keys needed
- **Python-native:** Easy integration with FastAPI backend
- **Good enough for prototype:** Handles hundreds of vectors efficiently
- **Easy migration:** Can migrate to Pinecone/Weaviate for production

**Production consideration:** Migrate to managed Pinecone or Weaviate for scale and reliability.

### Decision 3: Mock LLM Instead of Real Claude API

**Decision:** Use template-based mock LLM for prototype

**Rationale:**
- **No API costs:** Zero spend during development and demos
- **Consistent demos:** Same inputs always produce same outputs
- **Faster development:** No API latency, no rate limits
- **Offline capable:** Demo works without internet
- **Easy swap:** Architecture supports dropping in real Claude API later

**Implementation approach:**
- Service type classification using keyword matching
- Template-based labor/parts recommendations per service category
- Variance added based on vessel specs (larger vessels = more hours)
- Confidence calculated from similar job match quality

### Decision 4: Separate Frontend/Backend

**Decision:** Build as separate Next.js frontend + FastAPI backend

**Rationale:**
- **Flexibility:** Can demo frontend independently; can swap UIs
- **Production path:** Reflects how it would integrate with DockMaster
- **AI/ML stack:** Python backend better for ML tooling (embeddings, vector stores)
- **Team skills:** Allows parallel development if team scales

**Alternative considered:** Full-stack Next.js with API routes. Rejected due to Python ecosystem advantages for ML.

### Decision 5: Confidence Scoring Approach

**Decision:** Multi-factor confidence scoring based on:
1. Number of similar jobs retrieved (more = higher confidence)
2. Similarity scores of retrieved jobs (closer = higher confidence)
3. Variance in historical labor times (lower variance = higher confidence)
4. Match quality on vessel specifications (exact match = higher confidence)

**Formula:**
```
confidence = (
    0.3 * (min(similar_job_count, 20) / 20) +
    0.3 * avg_similarity_score +
    0.2 * (1 - labor_variance_normalized) +
    0.2 * vessel_match_score
)
```

**Rationale:**
- Provides actionable signal to service writers
- Lower confidence prompts more careful review
- Can be refined based on user feedback

### Decision 6: Parts Validation Strategy

**Decision:** All parts suggestions must exist in the mock parts catalog

**Rationale:**
- **Critical for trust:** Wrong part numbers destroy credibility
- **Integration path:** Real PartSmart integration will work the same way
- **Liability:** Reduces risk of ordering wrong parts

**Implementation:** Mock LLM suggests part categories; system matches to catalog items; only catalog items returned.

### Decision 7: Human-in-the-Loop Design

**Decision:** AI generates draft estimate; human reviews and modifies before finalizing

**Rationale:**
- **Reduces liability:** Human always makes final decision
- **Builds trust:** Users see AI as assistant, not replacement
- **Training signal:** Edits provide feedback for model improvement
- **Gradual adoption:** Users can start conservative and trust more over time

---

## Mock Data Strategy

### Synthetic Work Order Data (100 records)

Generate historical work orders covering:

**Vessel Types (5):**
- Runabouts (18-24')
- Cabin Cruisers (25-35')
- Center Consoles (20-30')
- Sailboats (25-40')
- Pontoon Boats (20-26')

**Engine Makes (6):**
- Mercury
- Yamaha
- Volvo Penta
- MerCruiser
- Suzuki
- Honda

**Service Categories (8):**
| Category | Example Services |
|----------|-----------------|
| Engine Service | Oil change, tune-up, winterization |
| Hull & Bottom | Cleaning, painting, repair |
| Electrical | Wiring, electronics, batteries |
| Mechanical | Steering, trim, hydraulics |
| Outboard Service | Impeller, lower unit, prop |
| Inboard Service | Transmission, shaft, exhaust |
| Annual Service | Spring commissioning, winterization |
| Diagnostic | Troubleshooting, inspection |

**Data Fields per Work Order:**
- `work_order_id`: Unique identifier
- `vessel_type`: Type of vessel
- `loa`: Length in feet
- `year`: Vessel year
- `engine_make`: Engine manufacturer
- `engine_model`: Engine model
- `service_category`: Category of service
- `service_description`: Text description
- `labor_items`: Array of {task, hours, rate}
- `parts_used`: Array of {part_number, description, quantity, price}
- `total_labor_hours`: Sum of labor
- `total_parts_cost`: Sum of parts
- `total_invoice`: Grand total
- `completion_date`: Date completed
- `region`: Geographic region
- `season`: Season when completed

### Mock Parts Catalog (300 items)

**Categories:**
| Category | Item Count | Examples |
|----------|------------|----------|
| Filters | 30 | Oil, fuel, air filters by engine make |
| Fluids | 25 | Engine oil, gear lube, coolant, hydraulic |
| Ignition | 35 | Spark plugs, coils, wires, modules |
| Impellers | 20 | Water pump impellers by engine |
| Belts & Hoses | 30 | Serpentine, raw water, fuel hoses |
| Electrical | 40 | Batteries, fuses, switches, wire |
| Bottom Paint | 20 | Ablative, hard, primers |
| Zincs/Anodes | 25 | Hull, prop, shaft zincs |
| Gaskets/Seals | 35 | Exhaust, water pump, lower unit |
| Props & Hardware | 40 | Props, hardware, bearings |

**Data Fields per Part:**
- `part_number`: Unique identifier
- `description`: Display name
- `category`: Part category
- `compatible_engines`: Array of compatible engine makes
- `list_price`: Price in USD
- `unit`: Unit of measure (each, quart, gallon, foot)

---

## Testing Strategy

### Unit Tests

| Component | Test Focus |
|-----------|------------|
| Embedding Service | Consistent embeddings, correct dimensions |
| RAG Engine | Returns relevant results, filters work correctly |
| Mock LLM | Valid JSON output, all required fields present |
| Confidence Scoring | Scores in 0-1 range, factors affect output correctly |
| Parts Catalog | Lookup works, returns valid parts only |

### Integration Tests

| Test Case | Description |
|-----------|-------------|
| End-to-end estimate | Full flow from API input to estimate response |
| Edge cases | Missing optional fields handled gracefully |
| Error handling | Invalid inputs return appropriate errors |
| Parts validation | Generated parts exist in catalog |

### Demo Scenarios (5 scripted)

| # | Scenario | Vessel | Service | Expected Confidence |
|---|----------|--------|---------|---------------------|
| 1 | Oil Change | 28' Cabin Cruiser, Volvo D4, 2019 | Annual oil and filter change | High (95%) |
| 2 | Bottom Paint | 32' Sailboat, 2015 | Hull cleaning and bottom paint | High (90%) |
| 3 | Electrical Issue | 24' Center Console, Yamaha F250, 2020 | Troubleshoot no-start condition | Medium (70%) |
| 4 | Winterization | 22' Runabout, MerCruiser 4.3, 2018 | Full winterization package | High (92%) |
| 5 | Unusual Vessel | 45' Custom, Caterpillar C9, 2010 | Engine service | Lower (60%) |

---

## Future Production Considerations

### Scaling Considerations

| Component | Prototype | Production |
|-----------|-----------|------------|
| Vector Store | ChromaDB (local) | Pinecone or Weaviate (managed) |
| LLM | Mock responses | Claude API (Anthropic) |
| Database | SQLite + JSON | PostgreSQL |
| Caching | None | Redis for common queries |
| Embeddings | sentence-transformers (local) | OpenAI or Anthropic embeddings |

### Real Claude API Integration

When ready to swap in real Claude API:

1. **Update `mock_llm.py`** to call Claude API instead of templates
2. **Add API key management** via environment variables
3. **Implement retry logic** for API failures
4. **Add response caching** to reduce costs
5. **Update prompts** for optimal Claude performance

### Security Considerations

| Area | Production Requirement |
|------|----------------------|
| API Keys | Secrets management (Vault, AWS Secrets Manager) |
| Data Isolation | Multi-tenant architecture, row-level security |
| HTTPS | TLS termination, certificate management |
| Authentication | OAuth 2.0 / SAML integration with DockMaster |
| Input Validation | Sanitize all user inputs |

### DockMaster Integration Points

| System | Integration Type | Notes |
|--------|-----------------|-------|
| DockMaster Web | Embedded iframe or API | Primary UI integration |
| DockMaster DB | Read-only access | Historical work orders |
| PartSmart | REST API | Real-time pricing |
| User Auth | SSO | Single sign-on with DockMaster |

### Data Pipeline (Production)

For production, historical work orders need:
1. **ETL pipeline** from DockMaster database
2. **Data cleaning** and normalization scripts
3. **Incremental embedding** updates (nightly batch)
4. **Feedback loop** for estimate accuracy tracking
5. **Anonymization** for cross-customer learning

---

## Project Structure Summary

```
valsoft/
├── AI Venture Builder - Case Study DockMaster.pdf  # Original case study
├── EstimateIQ_Business_Case_Deliverable.md         # Business case document
├── EstimateIQ_Prototype_Plan.md                    # This document
└── estimateiq-prototype/                           # Prototype code
    ├── frontend/                                   # Next.js application
    │   ├── src/
    │   │   ├── app/
    │   │   │   ├── page.tsx
    │   │   │   ├── layout.tsx
    │   │   │   └── estimate/
    │   │   │       └── new/page.tsx
    │   │   ├── components/
    │   │   │   ├── estimate/
    │   │   │   │   ├── VesselForm.tsx
    │   │   │   │   ├── ServiceRequestForm.tsx
    │   │   │   │   ├── EstimateDisplay.tsx
    │   │   │   │   ├── LineItemEditor.tsx
    │   │   │   │   └── ConfidenceIndicator.tsx
    │   │   │   └── ui/
    │   │   └── lib/
    │   │       ├── api.ts
    │   │       └── types.ts
    │   ├── package.json
    │   └── tailwind.config.js
    ├── backend/                                    # FastAPI application
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── api/
    │   │   │   └── routes/
    │   │   │       ├── estimates.py
    │   │   │       └── vessels.py
    │   │   ├── core/
    │   │   │   ├── config.py
    │   │   │   └── mock_llm.py
    │   │   ├── services/
    │   │   │   ├── estimate_generator.py
    │   │   │   ├── rag_engine.py
    │   │   │   ├── embedding_service.py
    │   │   │   └── parts_catalog.py
    │   │   ├── models/
    │   │   │   └── schemas.py
    │   │   └── data/
    │   │       ├── work_orders.json
    │   │       ├── parts_catalog.json
    │   │       └── labor_rates.json
    │   ├── scripts/
    │   │   ├── seed_data.py
    │   │   └── build_vector_store.py
    │   └── requirements.txt
    └── README.md                                   # Setup instructions
```

---

## Next Steps

To begin implementation:

1. **Create project directories** - Set up the folder structure
2. **Initialize frontend** - `npx create-next-app@latest frontend`
3. **Initialize backend** - Set up FastAPI with requirements.txt
4. **Generate seed data** - Run seed_data.py to create mock data
5. **Build incrementally** - Follow the 5-day phase plan

---

## Appendix: API Endpoint Specifications

### POST /api/estimates

**Request:**
```json
{
  "vessel": {
    "loa": 28,
    "year": 2019,
    "engine_make": "Volvo Penta",
    "engine_model": "D4-300",
    "hull_type": "fiberglass",
    "propulsion_type": "sterndrive"
  },
  "description": "Annual oil change and filter replacement",
  "service_category": "engine",
  "urgency": "routine"
}
```

**Response:**
```json
{
  "estimate_id": "est_abc123",
  "vessel": { ... },
  "service_description": "Annual oil change and filter replacement",
  "labor_items": [
    {
      "line_type": "labor",
      "description": "Oil and filter change - Volvo D4",
      "quantity": 1.5,
      "unit": "hours",
      "unit_price": 125.00,
      "total_price": 187.50,
      "confidence": 0.95
    }
  ],
  "parts_items": [
    {
      "line_type": "parts",
      "description": "Volvo Penta Oil Filter 21549542",
      "quantity": 1,
      "unit": "each",
      "unit_price": 42.99,
      "total_price": 42.99,
      "confidence": 0.98
    },
    {
      "line_type": "parts",
      "description": "Mobil 1 15W-40 Diesel Oil",
      "quantity": 2,
      "unit": "gallon",
      "unit_price": 32.99,
      "total_price": 65.98,
      "confidence": 0.95
    }
  ],
  "labor_subtotal": 187.50,
  "parts_subtotal": 108.97,
  "total_estimate": 296.47,
  "estimate_range": {
    "low": 266.82,
    "expected": 296.47,
    "high": 355.76
  },
  "confidence_score": 0.94,
  "similar_jobs_count": 23,
  "similar_jobs_summary": "Based on 23 similar oil changes on 25-30' vessels with Volvo D4 engines",
  "generated_at": "2026-03-13T10:30:00Z",
  "status": "draft"
}
```

### GET /api/similar-jobs

**Query Parameters:**
- `description`: Service description text
- `engine_make`: Filter by engine make
- `loa_min`: Minimum vessel length
- `loa_max`: Maximum vessel length
- `limit`: Number of results (default 10)

**Response:**
```json
{
  "jobs": [
    {
      "work_order_id": "WO-2024-1234",
      "similarity_score": 0.94,
      "vessel_type": "Cabin Cruiser",
      "loa": 27,
      "engine": "Volvo D4-260",
      "service_description": "Oil and filter change",
      "total_labor_hours": 1.5,
      "total_invoice": 285.00,
      "completion_date": "2024-09-15"
    }
  ],
  "total_count": 23
}
```

---

*Document prepared: March 2026*
*Status: Ready for Implementation*
