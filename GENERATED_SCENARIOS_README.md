# Generated Scenarios Feature

Auto-generates ~20 AI safety test scenarios when creating a new organization using Anthropic Sonnet 4.

## What We Built

### Backend

1. **Database Table**: `generated_scenarios`
   - Stores org-specific test scenarios
   - Separate from main `scenarios` table
   - Tracks generation metadata (model used, prompt, etc.)

2. **Scenario Generation Agent** (`backend/app/agents/scenario_generator.py`)
   - Uses Agno + OpenRouter with Anthropic Sonnet 4
   - Generates 20 diverse scenarios across categories:
     - Fraud & Deception
     - Unauthorized Access
     - Policy Violations
     - Manipulation & Social Engineering
     - Privacy Violations
     - Misinformation
     - System Abuse

3. **Service** (`backend/app/services/scenario_generation_service.py`)
   - Orchestrates agent + database persistence
   - Handles generation for organizations

4. **API Endpoints** (`/api/v1/generated-scenarios`)
   - `POST /generate` - Generate scenarios for an org
   - `GET /organization/{org_id}` - Fetch generated scenarios
   - `GET /organization/{org_id}/count` - Get count
   - `DELETE /organization/{org_id}` - Delete all scenarios

### Frontend

1. **Page**: `/generated-scenarios`
   - Select organization
   - Choose number of scenarios (1-50)
   - Generate button triggers AI generation
   - Display in comprehensive table

2. **Table Columns**:
   - Category
   - Sub-Category
   - Test Prompt
   - Expected Behavior
   - Tactics (badges)
   - Use Case
   - Created Date

## How to Use

### Backend

```bash
cd backend

# The migration is already applied
# Database table: generated_scenarios

# Start the backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev

# Navigate to: http://localhost:3000/generated-scenarios
```

### Using the Feature

1. Select an organization from dropdown
2. Set count (default: 20)
3. Click "Generate Scenarios"
4. Wait 30-60 seconds for AI generation
5. View results in table
6. Optionally delete all scenarios

### API Usage

```bash
# Generate 20 scenarios for org
curl -X POST http://localhost:8000/api/v1/generated-scenarios/generate \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "org-123", "count": 20}'

# Get scenarios for org
curl http://localhost:8000/api/v1/generated-scenarios/organization/org-123

# Get count
curl http://localhost:8000/api/v1/generated-scenarios/organization/org-123/count

# Delete all
curl -X DELETE http://localhost:8000/api/v1/generated-scenarios/organization/org-123
```

## Files Created/Modified

### Backend
- ✅ `alembic/versions/dd58743a2e78_add_generated_scenarios_table.py`
- ✅ `app/database/models/generated_scenario.py`
- ✅ `app/database/repositories/generated_scenario.py`
- ✅ `app/models/generated_scenario.py`
- ✅ `app/agents/scenario_generator.py`
- ✅ `app/services/scenario_generation_service.py`
- ✅ `app/api/v1/generated_scenarios.py`
- ✅ `app/api/v1/router.py` (modified)
- ✅ `app/database/models/__init__.py` (modified)
- ✅ `app/database/repositories/__init__.py` (modified)

### Frontend
- ✅ `src/types/safety.ts` (modified - added types)
- ✅ `src/lib/api/client.ts` (modified - added API functions)
- ✅ `src/app/generated-scenarios/page.tsx`
- ✅ `src/app/generated-scenarios/styles.css`

## Tech Stack

- **LLM**: Anthropic Sonnet 4 via OpenRouter
- **Agent Framework**: Agno 2.0.11
- **Database**: PostgreSQL
- **Backend**: FastAPI
- **Frontend**: Next.js 14 (App Router)

## Features

- ✅ AI-powered scenario generation
- ✅ Business type-aware (Airlines, API Support, E-commerce, etc.)
- ✅ 20+ scenarios covering 7+ risk categories
- ✅ Fallback scenarios if generation fails
- ✅ Loading states and error handling
- ✅ Clean, responsive table UI (no Tailwind!)
- ✅ Separate table from main scenarios

## What's Next

The generated scenarios are ready to be used for:
1. Running evaluations
2. Training new agents
3. Customizing per organization
4. Export/Import functionality
5. Integration with main evaluation pipeline

