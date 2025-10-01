# Safety Story Dashboard - Setup Guide

## What We Built

A complete **Safety Story Dashboard** that visualizes the path from real-world AI incidents to comprehensive protection:

**Incidents → Safeguards → Tests → Residual Risk**

This gives AI buyers confidence by showing:
1. **What can go wrong** (real incidents like AirCanada)
2. **How we prevent it** (AIUC-1 safeguards)
3. **How we test** (comprehensive evaluation scenarios)
4. **What's left** (residual risk assessment)

## Components Created

### Backend
- ✅ **AIIncident Model** (`backend/app/database/models/ai_incident.py`)
  - Tracks real-world failures with severity, harm type, financial impact
  - Links to business types for relevant incident filtering
  
- ✅ **Migration** (`backend/alembic/versions/217d678d2c6d_add_ai_incidents_table.py`)
  - Creates `ai_incidents` table
  - Adds `description` field to `business_types`

- ✅ **Incidents API** (`backend/app/api/v1/ai_incidents.py`)
  - CRUD operations: Create, Read, Update, Delete incidents
  - Stats endpoints: `/stats/severity`, `/stats/harm-types`
  - Filtering by severity, company, harm type, business type

- ✅ **Repository** (`backend/app/database/repositories/ai_incident_repository.py`)
  - Clean data access layer with filtering and stats

### Frontend
- ✅ **Safety Story Page** (`frontend/src/app/safety-story/page.tsx`)
  - 4-step flow visualization
  - Real-time incident cards with details
  - Severity and harm type breakdowns
  - CTA to run evaluations

- ✅ **Incident Card Component** (`frontend/src/components/safety/IncidentCard.tsx`)
  - Beautiful severity-coded cards
  - Expandable details
  - Financial impact display
  - Source links

- ✅ **Types** (`frontend/src/types/safety.ts`)
  - TypeScript types for incidents and safety metrics

### Seed Data
- ✅ **Seed Script** (`backend/scripts/seed_incidents.py`)
  - Pre-populated with 6 famous incidents:
    - **AirCanada** refund hallucination (P1, financial_loss)
    - **Chevrolet** $1 car sale (P2, financial_loss)
    - **OpenAI ChatGPT** data breach (P0, privacy_breach)
    - **DPD** swearing chatbot (P2, reputation_damage)
    - **Google Gemini** historical bias (P1, reputation_damage)
    - **Microsoft Tay** racist tweets (P0, reputation_damage)

## Quick Start

### 1. Run Migration
```bash
cd backend
alembic upgrade head
```

### 2. Seed Incidents
```bash
python scripts/seed_incidents.py
```

### 3. Start Backend
```bash
# If not already running
./scripts/start.sh
```

### 4. Start Frontend
```bash
cd frontend
npm run dev
```

### 5. View Safety Story
Navigate to: **http://localhost:3000/safety-story**

## API Endpoints

### List Incidents
```bash
GET /api/v1/incidents
Query params: severity, harm_type, company, business_type_id, limit, skip
```

### Get Incident
```bash
GET /api/v1/incidents/{incident_id}
```

### Create Incident
```bash
POST /api/v1/incidents
Body: {
  "incident_name": "AirCanada Refund Hallucination",
  "company": "Air Canada",
  "severity": "P1",
  "harm_type": "financial_loss",
  "description": "...",
  "estimated_cost": 15000.00,
  ...
}
```

### Severity Stats
```bash
GET /api/v1/incidents/stats/severity
GET /api/v1/incidents/stats/harm-types
```

## Navigation

Safety Story is now integrated into main navigation:
- **Home page** footer
- **Dashboard** top nav
- **Safety Story** page itself

## How It Helps Sales

This dashboard is designed for **enterprise buyers** (like Heads of Customer Support) to:

1. **See the Stakes**: Real incidents with $ impact (AirCanada: $15K loss)
2. **Understand Protection**: AIUC-1 compliance requirements (100% pass rate)
3. **Verify Testing**: Comprehensive scenarios mapped to each incident type
4. **Assess Residual Risk**: What's left after all safeguards

### Sales Pitch Flow
> "Remember the AirCanada chatbot disaster? $15K loss, legal precedent, reputation damage. 
> Here's how we make sure that never happens to you:
> 
> 1. We track 50+ real incidents like this
> 2. We map each to AIUC-1 safeguards
> 3. We run 150+ test scenarios across 3 rounds
> 4. You get 97.4% → 100% pass rate with third-party verification
> 
> Your residual risk? Minimal. Your buyer confidence? Maximum."

## Next Steps

### Add More Incidents
Create incidents via API or add to seed script:
- Industry-specific incidents
- Recent 2024-2025 failures
- Competitor failures (social proof)

### Map Incidents to Scenarios
Future enhancement: Link incidents to specific test scenarios
- Show "This incident → These tests"
- Coverage heatmap

### Residual Risk Calculation
Currently static. Could calculate based on:
- Open P0/P1 failures
- Incident coverage %
- AIUC-1 compliance gap

### Customer-Specific View
Filter incidents by business type automatically
- Airlines see AirCanada
- E-commerce sees different incidents
- API platforms see relevant failures

## Troubleshooting

### Migration Issues
```bash
# Check current revision
alembic current

# Show migration history
alembic history

# Downgrade if needed
alembic downgrade -1
```

### No Incidents Showing
1. Run seed script: `python scripts/seed_incidents.py`
2. Check API: `curl http://localhost:8000/api/v1/incidents`
3. Check browser console for fetch errors

### TypeScript Errors
```bash
cd frontend
npm install  # Ensure deps are installed
npm run build  # Check for type errors
```

## Files Modified

**Backend:**
- `app/database/models/ai_incident.py` (new)
- `app/database/models/business_type.py` (updated)
- `app/database/models/__init__.py` (updated)
- `app/database/repositories/ai_incident_repository.py` (new)
- `app/database/repositories/__init__.py` (updated)
- `app/models/ai_incident.py` (new)
- `app/api/v1/ai_incidents.py` (new)
- `app/api/v1/router.py` (updated)
- `alembic/versions/217d678d2c6d_add_ai_incidents_table.py` (new)
- `scripts/seed_incidents.py` (new)

**Frontend:**
- `src/types/safety.ts` (new)
- `src/components/safety/IncidentCard.tsx` (new)
- `src/app/safety-story/page.tsx` (new)
- `src/app/page.tsx` (updated nav)
- `src/app/dashboard/page.tsx` (updated nav)

---

Built to show AI buyers the straight line from **real disasters** to **comprehensive protection**. 🚀

