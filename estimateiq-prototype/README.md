# EstimateIQ Prototype

AI-powered service estimate generator for DockMaster's marine service operations.

## Overview

EstimateIQ transforms the labor-intensive process of creating marine repair estimates into a 5-minute AI-assisted workflow. This prototype demonstrates the core value proposition using mock data and a template-based generation system.

## Project Structure

```
estimateiq-prototype/
├── start.sh                     # Startup script for both servers
├── frontend/                    # Next.js 14 application
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   ├── components/         # React components
│   │   │   ├── estimate/      # Estimate-specific components (Phase 4)
│   │   │   └── ui/            # Shared UI components
│   │   └── lib/
│   │       ├── api.ts         # API client functions
│   │       └── types.ts       # TypeScript type definitions
│   └── package.json
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/        # API endpoints
│   │   │       ├── estimates.py      # Estimate generation
│   │   │       ├── similar_jobs.py   # RAG search endpoints
│   │   │       └── vessels.py        # Vessel lookup
│   │   ├── core/
│   │   │   ├── config.py      # Configuration settings
│   │   │   └── mock_llm.py    # Template-based estimate generation
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic data models
│   │   ├── services/
│   │   │   ├── embedding_service.py   # Text embeddings & vector store
│   │   │   ├── rag_engine.py          # Similar job retrieval
│   │   │   ├── parts_catalog.py       # Parts lookup & validation
│   │   │   └── estimate_generator.py  # Main orchestration service
│   │   ├── data/              # Mock data files
│   │   │   ├── work_orders.json       # 100 historical work orders
│   │   │   ├── parts_catalog.json     # 300 marine parts
│   │   │   ├── labor_rates.json       # Labor rate configuration
│   │   │   └── estimate_templates.json # Service templates (8 categories)
│   │   └── main.py            # FastAPI entry point
│   ├── chroma_db/             # Vector store persistence
│   ├── scripts/
│   │   └── seed_data.py       # Data generation script
│   ├── tests/                 # Test suite (221 tests)
│   └── requirements.txt
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### One-Command Startup (Recommended)

The easiest way to start both servers is with the included startup script:

```bash
./start.sh
```

This will:
- Check prerequisites (Python, Node.js, npm)
- Create a Python virtual environment if needed
- Install all dependencies
- Start both backend and frontend servers
- Provide URLs for accessing the application

Press `Ctrl+C` to stop both servers.

### Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pydantic-settings

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:3000

## API Endpoints

### Estimates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/estimates` | Generate a new estimate |
| GET | `/api/estimates/{id}` | Get an estimate by ID (Phase 2) |

### Vessels

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vessels` | List all vessels |
| GET | `/api/vessels/{id}` | Get vessel by ID |
| GET | `/api/vessels/search/{query}` | Search vessels |

### Similar Jobs (RAG)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/similar-jobs?description=...` | Find similar jobs by description |
| POST | `/api/similar-jobs/with-vessel` | Find similar jobs with vessel context |
| GET | `/api/similar-jobs/{work_order_id}` | Get full work order details |
| GET | `/api/similar-jobs/stats/labor-hours?description=...` | Get labor statistics |
| GET | `/api/similar-jobs/stats/parts-patterns?description=...` | Get parts patterns |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Root endpoint |

## Example API Usage

### Generate an Estimate

```bash
curl -X POST http://localhost:8000/api/estimates \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Response

```json
{
  "estimate_id": "est_abc123def456",
  "vessel": { ... },
  "service_description": "Annual oil change and filter replacement",
  "labor_items": [
    {
      "line_type": "labor",
      "description": "Service labor - Annual oil change and filter replacement",
      "quantity": 2.0,
      "unit": "hours",
      "unit_price": 125.00,
      "total_price": 250.00,
      "confidence": 0.85
    }
  ],
  "parts_items": [
    {
      "line_type": "parts",
      "description": "Oil Filter",
      "quantity": 1,
      "unit": "each",
      "unit_price": 42.99,
      "total_price": 42.99,
      "confidence": 0.90,
      "part_number": "OF-001"
    }
  ],
  "labor_subtotal": 250.00,
  "parts_subtotal": 108.97,
  "total_estimate": 358.97,
  "estimate_range": {
    "low": 323.07,
    "expected": 358.97,
    "high": 430.76
  },
  "confidence_score": 0.87,
  "similar_jobs_count": 15,
  "similar_jobs_summary": "Based on 15 similar jobs on 26-30' vessels with Volvo Penta engines",
  "status": "draft"
}
```

## Mock Data

The prototype includes synthetic data for demonstration:

### Work Orders (100 records)

Historical service jobs covering:
- 5 vessel types (Runabout, Cabin Cruiser, Center Console, Sailboat, Pontoon)
- 6 engine makes (Mercury, Yamaha, Volvo Penta, MerCruiser, Suzuki, Honda)
- 8 service categories (engine, hull, electrical, mechanical, outboard, inboard, annual, diagnostic)
- 6 geographic regions

### Parts Catalog (300 items)

Marine parts across categories:
- Filters (oil, fuel, air)
- Fluids (engine oils, gear oils)
- Ignition (spark plugs)
- Impellers
- Belts & Hoses
- Electrical (batteries, pumps, lights)
- Bottom Paint
- Zincs/Anodes
- Gaskets/Seals
- Props & Hardware
- Seasonal (antifreeze, stabilizer)

## Development Status

### Phase 1 - Foundation ✅

- [x] Project structure setup
- [x] FastAPI backend with basic endpoints
- [x] Next.js frontend initialized
- [x] Pydantic data models
- [x] Synthetic work order data (100 records)
- [x] Mock parts catalog (300 items)
- [x] TypeScript type definitions
- [x] API client library

### Phase 2 - RAG Engine ✅

- [x] ChromaDB vector store setup
- [x] Embedding service with sentence-transformers
- [x] Similar jobs retrieval endpoint (`/api/similar-jobs`)
- [x] Work order indexing (100 documents)
- [x] Similarity scoring and vessel-specific boosting
- [x] Confidence calculation algorithm
- [x] Labor statistics and parts patterns endpoints

### Phase 3 - Mock LLM & Estimate Generation ✅

- [x] Template-based estimate generation (8 service categories)
- [x] Service type classification with keyword matching
- [x] Integrate RAG results into estimate endpoint
- [x] Parts catalog validation (all parts grounded in catalog)
- [x] Confidence scoring (combines RAG, LLM, and template confidence)
- [x] EstimateGenerator service orchestrating RAG + Mock LLM + Parts Catalog
- [x] Labor hour adjustments by LOA and similar job history
- [x] Estimate range calculation (low/expected/high)

### Phase 4 (Next) - Frontend UI

- [ ] Install shadcn/ui components
- [ ] Vessel input form with validation
- [ ] Service request form
- [ ] Estimate display component
- [ ] Line item editor
- [ ] Confidence indicators
- [ ] Estimate range visualization

### Phase 5 - Polish & Demo

- [ ] Loading states and error handling
- [ ] 5 demo scenarios
- [ ] Final testing
- [ ] Demo documentation

## Technology Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components (to be installed in Phase 4)

### Backend
- FastAPI
- Pydantic v2
- ChromaDB (vector store for RAG)
- sentence-transformers (text embeddings)
- Template-based Mock LLM (estimate generation)

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# API Settings
DEBUG=true

# CORS (frontend URL)
CORS_ORIGINS=["http://localhost:3000"]

# LLM (Future)
USE_REAL_LLM=false
ANTHROPIC_API_KEY=your-api-key-here
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## License

Proprietary - Valsoft Corporation

## Contact

AI Venture Builder Team - Valsoft Corporation
