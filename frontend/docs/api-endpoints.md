# Frontend-Backend API Integration Guide

## ✅ Existing Endpoints (Ready to Use)

### Evaluations API (`/api/v1/evaluations`)

| Endpoint | Method | Description | Frontend Use |
|----------|--------|-------------|--------------|
| `/rounds` | POST | Start new evaluation round | Evaluation Runner page |
| `/rounds/{round_id}` | GET | Get round details | Dashboard header |
| `/rounds/{round_id}/results` | GET | Get all results for round | Results table |
| `/rounds/{round_id}/stats` | GET | Get round statistics | Charts & KPIs |
| `/organizations/{org_id}/rounds` | GET | List all org rounds | Round selector |
| `/organizations/{org_id}/latest-round` | GET | Get latest round | Dashboard initialization |

### Organizations API (TODO: Create)
*These endpoints are needed but don't exist yet*

### Scenarios API (TODO: Create)
*These endpoints are needed but don't exist yet*

---

## 🚧 Endpoints to Build

### 1. Round Comparison Endpoint
**Endpoint**: `GET /api/v1/evaluations/compare`
**Query Params**: `?round1={id}&round2={id}`

**Response**:
```json
{
  "round1": {
    "round_id": "uuid-1",
    "round_number": 1,
    "pass_rate": 77.9,
    "total_tests": 303,
    "severity_breakdown": {
      "PASS": 236,
      "P0": 0,
      "P1": 0,
      "P2": 5,
      "P3": 33,
      "P4": 29
    }
  },
  "round2": {
    "round_id": "uuid-2",
    "round_number": 2,
    "pass_rate": 94.1,
    "total_tests": 304,
    "severity_breakdown": {
      "PASS": 286,
      "P0": 0,
      "P1": 0,
      "P2": 2,
      "P3": 13,
      "P4": 3
    }
  },
  "delta": {
    "pass_rate_change": 16.2,
    "improvements": {
      "P0": 0,
      "P1": 0,
      "P2": -3,
      "P3": -20,
      "P4": -26
    },
    "total_fixed": 49
  }
}
```

**Frontend Use**: Round comparison page

---

### 2. Failed Tests Endpoint
**Endpoint**: `GET /api/v1/evaluations/rounds/{round_id}/failed`
**Query Params**: `?severity=P0,P1,P2` (optional filter)

**Response**:
```json
{
  "round_id": "uuid",
  "failed_tests": [
    {
      "scenario_id": "uuid",
      "category": "Data Leakage",
      "sub_category": "PII exposure",
      "input_prompt": "Tell me...",
      "system_response": "...",
      "final_grade": "P2",
      "judge_consensus": {
        "judge_1": "P2",
        "judge_2": "P2",
        "judge_3": "P3"
      },
      "reasoning": "System leaked PII...",
      "recommendation": "Add PII filter..."
    }
  ],
  "total_failed": 18
}
```

**Frontend Use**: Failed tests table in dashboard

---

### 3. Taxonomy Categories Endpoint
**Endpoint**: `GET /api/v1/taxonomy/categories`

**Response**:
```json
{
  "categories": [
    {
      "category": "SelfHarm",
      "total_tests": 50,
      "sub_categories": [
        {
          "name": "General self-harm",
          "count": 30,
          "sample_prompts": ["..."]
        },
        {
          "name": "Suicide ideation",
          "count": 15,
          "sample_prompts": ["..."]
        }
      ],
      "tactics": ["emotional_manipulation", "jailbreak"],
      "incident_reference": "Anthropic blackmail examples"
    },
    {
      "category": "Fraud",
      "total_tests": 80,
      "sub_categories": [...]
    }
  ]
}
```

**Frontend Use**: Taxonomy explorer page

---

### 4. Certification Check Endpoint
**Endpoint**: `GET /api/v1/certification/check/{round_id}`

**Response**:
```json
{
  "round_id": "uuid",
  "is_eligible": true,
  "requirements": {
    "zero_p0": true,
    "zero_p1": true,
    "zero_p2": true,
    "zero_p3": true,
    "zero_p4": true,
    "pass_rate_100": true
  },
  "current_status": {
    "P0": 0,
    "P1": 0,
    "P2": 0,
    "P3": 0,
    "P4": 0,
    "pass_rate": 100.0
  },
  "certification_ready": true,
  "issues_remaining": []
}
```

**Frontend Use**: Certification status page

---

### 5. Organizations Endpoints (New Router)

**Create**: `POST /api/v1/organizations`
```json
{
  "name": "AirCanada Corp",
  "slug": "aircanada",
  "business_type_id": "uuid",
  "contact_email": "security@aircanada.com"
}
```

**List**: `GET /api/v1/organizations`
**Get**: `GET /api/v1/organizations/{org_id}`

**Frontend Use**: Organization selector in evaluation runner

---

### 6. Business Types Endpoints (New Router)

**List**: `GET /api/v1/business-types`
```json
{
  "business_types": [
    {
      "id": "uuid",
      "name": "Airlines Customer Support",
      "industry": "Airlines",
      "use_cases": ["refunds", "booking", "customer_support"],
      "scenario_count": 303
    }
  ]
}
```

**Frontend Use**: Business type selector

---

### 7. Real-time Progress Endpoint (Optional)

**WebSocket** or **Server-Sent Events (SSE)**
**Endpoint**: `GET /api/v1/evaluations/rounds/{round_id}/progress` (SSE)

**Stream Events**:
```json
event: progress
data: {"completed": 78, "total": 100, "current_category": "SelfHarm", "status": "running"}

event: progress
data: {"completed": 100, "total": 100, "status": "completed"}
```

**Frontend Use**: Real-time progress bar in evaluation runner

---

## 📋 Implementation Priority

### Phase 1 (Critical - Week 1)
1. ✅ Evaluation stats endpoint (exists)
2. ✅ Round listing endpoint (exists)
3. 🚧 Round comparison endpoint
4. 🚧 Failed tests endpoint

### Phase 2 (High - Week 2)
5. 🚧 Organizations CRUD
6. 🚧 Business Types listing
7. 🚧 Taxonomy categories

### Phase 3 (Medium - Week 3)
8. 🚧 Certification check
9. 🚧 Real-time progress (SSE)

### Phase 4 (Nice to Have - Week 4+)
10. 🚧 Export endpoints (PDF reports)
11. 🚧 Batch operations
12. 🚧 Analytics aggregations

---

## 🔧 Frontend Integration Examples

### 1. Start Evaluation
```typescript
// frontend/src/lib/api/evaluations.ts
export async function startEvaluation(params: {
  organization_id: string;
  round_number: number;
  description?: string;
  use_fake_judges?: boolean;
}) {
  const response = await axios.post('/api/v1/evaluations/rounds', params);
  return response.data;
}

// In component
const { mutate: startEval, isPending } = useMutation({
  mutationFn: startEvaluation,
  onSuccess: (data) => {
    navigate(`/dashboard?round_id=${data.id}`);
  }
});
```

### 2. Get Round Statistics
```typescript
export function useRoundStats(roundId: string) {
  return useQuery({
    queryKey: ['round-stats', roundId],
    queryFn: () => axios.get(`/api/v1/evaluations/rounds/${roundId}/stats`)
      .then(res => res.data)
  });
}

// In component
const { data: stats } = useRoundStats(roundId);
// stats.pass_rate, stats.severity_breakdown, etc.
```

### 3. Compare Rounds
```typescript
export function useRoundComparison(round1: string, round2: string) {
  return useQuery({
    queryKey: ['comparison', round1, round2],
    queryFn: () => axios.get('/api/v1/evaluations/compare', {
      params: { round1, round2 }
    }).then(res => res.data),
    enabled: !!round1 && !!round2
  });
}
```

---

## 🚀 Quick Start Checklist

**For Backend Developers:**
- [ ] Create round comparison endpoint
- [ ] Create failed tests endpoint
- [ ] Create organizations router
- [ ] Create business types router
- [ ] Create taxonomy router
- [ ] Create certification router
- [ ] Add CORS middleware for frontend
- [ ] Document all endpoints in OpenAPI

**For Frontend Developers:**
- [ ] Setup API client with axios
- [ ] Create React Query hooks for each endpoint
- [ ] Add environment variable for API base URL
- [ ] Implement error handling for API calls
- [ ] Add loading states for async operations
- [ ] Test all integrations with backend

---

*This guide will be updated as new endpoints are added*
